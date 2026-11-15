""" api_client_executor.py — v1
IMPLEMENTATION CANDIDATE — READY FOR INTEGRATION TESTING
"""
import hashlib
import http.client
import ipaddress
import json
import socket
import ssl
from urllib.parse import urlsplit

try:
    import rfc8785
except ImportError:
    rfc8785 = None

class JCSValidationError(ValueError):
    pass

class TransportError(Exception):
    pass

def _reject_constants(text: str):
    # Rejeita NaN / Infinity que o json.loads aceita como extensao
    import re
    if re.search(r'(?<![A-Za-z0-9_"\'])NaN(?![A-Za-z0-9_])', text):
        raise JCSValidationError("NON_JSON_CONSTANT: NaN")
    if re.search(r'(?<![A-Za-z0-9_"\'])-?Infinity(?![A-Za-z0-9_])', text):
        raise JCSValidationError("NON_JSON_CONSTANT: Infinity")

def _parse_no_dupes(text: str):
    _reject_constants(text)
    def hook(pairs):
        obj = {}
        for k, v in pairs:
            if k in obj:
                raise JCSValidationError(f"DUPLICATE_KEY: {k}")
            obj[k] = v
        return obj
    try:
        return json.loads(text, object_pairs_hook=hook, parse_constant=lambda x: (_ for _ in ()).throw(JCSValidationError(f"NON_JSON_CONSTANT: {x}")))
    except JCSValidationError:
        raise
    except Exception as e:
        raise JCSValidationError(f"INVALID_JSON: {e}")

def canonicalize_jcs_from_text(text: str) -> bytes:
    if rfc8785 is None:
        raise JCSValidationError("MISSING_DEPENDENCY: rfc8785")
    obj = _parse_no_dupes(text)
    return rfc8785.dumps(obj)

def hash_canonical_json_text(text: str) -> dict:
    canon = canonicalize_jcs_from_text(text)
    return {
        "canonical_bytes": canon,
        "canonical_utf8": canon.decode("utf-8"),
        "len_bytes": len(canon),
        "sha256": hashlib.sha256(canon).hexdigest(),
    }

def validate_url(url: str):
    u = urlsplit(url)
    if u.scheme not in ("http", "https"):
        raise TransportError(f"URL_SCHEME_REJECTED: {u.scheme}")
    if u.username or u.password:
        raise TransportError("URL_USERINFO_REJECTED")
    if u.fragment:
        raise TransportError("URL_FRAGMENT_REJECTED")
    if not u.hostname:
        raise TransportError("URL_HOST_MISSING")
    port = u.port if u.port else (443 if u.scheme == "https" else 80)
    path = u.path or "/"
    if u.query:
        path += "?" + u.query
    return u.hostname, u.scheme, port, path

def _default_resolver(host, port):
    try:
        infos = socket.getaddrinfo(host, port, proto=socket.IPPROTO_TCP)
    except socket.gaierror as e:
        raise TransportError(f"DNS_ERROR: {e}")
    addrs = []
    for _, _, _, _, sockaddr in infos:
        addrs.append(sockaddr[0])
    # Dedup preservando ordem
    seen = set()
    out = []
    for a in addrs:
        if a not in seen:
            seen.add(a)
            out.append(a)
    return out

class ApiClientExecutor:
    def __init__(self, resolver=None, timeout=10):
        self.resolver = resolver or _default_resolver
        self.timeout = timeout

    def execute(self, method: str, url: str, body: str | None = None, headers: dict | None = None):
        host, scheme, port, path = validate_url(url)
        addrs = self.resolver(host, port)
        if not addrs:
            raise TransportError("DNS_EMPTY")
        last_err = None
        for ip in addrs:
            try:
                if scheme == "https":
                    ctx = ssl.create_default_context()
                    conn = http.client.HTTPSConnection(ip, port, timeout=self.timeout, context=ctx)
                    conn.set_tunnel(host, port)
                    # SNI / Host corretos via tunnel + header
                else:
                    conn = http.client.HTTPConnection(ip, port, timeout=self.timeout)
                h = dict(headers or {})
                h.setdefault("Host", host if port in (80, 443) else f"{host}:{port}")
                h.setdefault("Connection", "close")
                conn.request(method, path, body=body, headers=h)
                resp = conn.getresponse()
                data = resp.read()
                conn.close()
                return {"status": resp.status, "headers": dict(resp.getheaders()), "body": data, "peer_ip": ip}
            except http.client.HTTPException as e:
                raise TransportError(f"HTTP_EXCEPTION: {e}")
            except Exception as e:
                last_err = e
                continue
        raise TransportError(f"CONNECT_FAILED: {last_err}")