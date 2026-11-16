# XA-TRUST E5 v1.1.6.3 - TUDO EM 1 ARQUIVO
# pip install rfc8785==0.1.2 cryptography==42.0.5
# python e5_all_in_one.py
import hashlib, re, os, tempfile, json
import rfc8785
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

HEX64 = re.compile(r"^[0-9a-f]{64}$")
HEX128 = re.compile(r"^[0-9a-f]{128}$")

def key_fingerprint(b):
    assert len(b) == 32
    return "sha256:" + hashlib.sha256(b).hexdigest()

def verify_e5(receipt, claim, keys, manifest_bytes, read_fn, root):
    if receipt.get("claim_id") != claim.get("claim_id"): return "FAIL"
    if receipt.get("claim_scope") != claim.get("claim_scope"): return "FAIL"
    payload = receipt.get("signed_payload")
    if not isinstance(payload, dict): return "INSUFFICIENT_EVIDENCE"
    try:
        canon = rfc8785.dumps(payload)
        if isinstance(canon, str): canon = canon.encode()
    except Exception: return "FAIL"
    if receipt.get("signed_payload_sha256") != hashlib.sha256(canon).hexdigest(): return "FAIL"
    if payload.get("claim_id") != claim.get("claim_id"): return "FAIL"
    if payload.get("claim_scope") != claim.get("claim_scope"): return "FAIL"
    if payload.get("manifest_sha256") != receipt.get("manifest_sha256"): return "FAIL"
    sig_hex = receipt.get("signature", "")
    if not HEX128.match(sig_hex): return "FAIL"
    sig = bytes.fromhex(sig_hex)
    key = keys.get(receipt.get("public_key_id"))
    if not key: return "NOT_VERIFIED"
    pub = key.get("public_key_bytes")
    if not isinstance(pub, bytes) or len(pub) != 32: return "FAIL"
    if receipt.get("fingerprint") != key_fingerprint(pub): return "FAIL"
    if "E5" not in key.get("authorized_for", []) or key.get("revoked"): return "FAIL"
    try:
        Ed25519PublicKey.from_public_bytes(pub).verify(sig, canon)
    except Exception: return "FAIL"
    if manifest_bytes is None: return "INSUFFICIENT_EVIDENCE"
    if hashlib.sha256(manifest_bytes).hexdigest() != receipt.get("manifest_sha256"): return "FAIL"
    try:
        m = json.loads(manifest_bytes)
        marts = {(a["path"], a["sha256"]) for a in m.get("artifacts", [])}
    except Exception: return "FAIL"
    ex = receipt.get("examined_artifacts")
    if not isinstance(ex, list) or len(ex) == 0: return "INSUFFICIENT_EVIDENCE"
    seen = set()
    for art in ex:
        p = art.get("path")
        if not p or p in seen: return "FAIL"
        seen.add(p)
        ar = os.path.realpath(root)
        ap = os.path.realpath(os.path.join(root, p))
        if not (ap == ar or ap.startswith(ar + os.sep)): return "FAIL"
        if type(art.get("bytes_read")) is not int or art["bytes_read"] < 0: return "FAIL"
        if not HEX64.match(art.get("sha256", "")): return "FAIL"
        if (p, art["sha256"]) not in marts: return "FAIL"
        try: data = read_fn(p)
        except Exception: return "INSUFFICIENT_EVIDENCE"
        if len(data) != art["bytes_read"]: return "FAIL"
        if hashlib.sha256(data).hexdigest() != art["sha256"]: return "FAIL"
    if marts != {(a["path"], a["sha256"]) for a in ex}: return "INSUFFICIENT_EVIDENCE"
    return "PASS"

priv = Ed25519PrivateKey.generate()
pub_bytes = priv.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
KEY_ID = "key-e5-test-01"
KEYS = {KEY_ID: {"public_key_bytes": pub_bytes, "fingerprint": key_fingerprint(pub_bytes), "authorized_for": ["E5"], "revoked": False}}
CLAIM = {"claim_id": "CLM-001", "claim_scope": {"repository": "github.com/xa-finance/core", "workflow": "verify", "commit_sha": "c9eb1f2f"}}
MARTS = [{"path": "src/runtime/execution.py", "sha256": hashlib.sha256(b"print(1)\n").hexdigest()}]
MBYTES = rfc8785.dumps({"artifacts": MARTS})
if isinstance(MBYTES, str): MBYTES = MBYTES.encode()
MHASH = hashlib.sha256(MBYTES).hexdigest()

def build(op=None, orc=None):
    pay = {"claim_id": "CLM-001", "claim_scope": CLAIM["claim_scope"], "manifest_sha256": MHASH}
    if op: pay.update(op)
    canon = rfc8785.dumps(pay)
    if isinstance(canon, str): canon = canon.encode()
    r = {"claim_id": "CLM-001", "claim_scope": CLAIM["claim_scope"], "public_key_id": KEY_ID, "fingerprint": key_fingerprint(pub_bytes), "signed_payload_sha256": hashlib.sha256(canon).hexdigest(), "signed_payload": pay, "signature": priv.sign(canon).hex(), "manifest_sha256": MHASH, "examined_artifacts": [{"path": "src/runtime/execution.py", "sha256": MARTS[0]["sha256"], "bytes_read": 9}]}
    if orc: r.update(orc)
    return r

def run(receipt, mb=MBYTES, keys=None, files=None):
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "src/runtime"), exist_ok=True)
        open(os.path.join(tmp, "src/runtime/execution.py"), "wb").write(b"print(1)\n")
        if files: files(tmp)
        def read_fn(p):
            full = os.path.realpath(os.path.join(tmp, p))
            with open(full, "rb") as fh: return fh.read()
        return verify_e5(receipt, CLAIM, keys or KEYS, mb, read_fn, tmp)

assert rfc8785.dumps({"a": 1, "b": "é"}) == b'{"a":1,"b":"\xc3\xa9"}'
print("JCS-001 OK")
assert rfc8785.dumps({"value": 1.5}) == b'{"value":1.5}'
print("JCS-002 OK")
try: rfc8785.dumps({"value": float("nan")}); raise AssertionError("NaN")
except Exception: print("NEG-016 OK")
assert run(build()) == "PASS"; print("POS-E5-001 PASS")
assert run(build(op={"claim_id": "CLM-999"})) == "FAIL"; print("NEG-006 OK")
assert run(build(op={"claim_scope": {"repository": "x", "workflow": "verify", "commit_sha": "c9eb1f2f"}})) == "FAIL"; print("NEG-007 OK")
assert run(build(op={"manifest_sha256": "0"*64})) == "FAIL"; print("NEG-008 OK")
assert run(build(), mb=None) == "INSUFFICIENT_EVIDENCE"; print("NEG-009 OK")
assert run(build(orc={"manifest_sha256": "0"*64})) == "FAIL"; print("NEG-010 OK")
assert run(build(orc={"examined_artifacts": []})) == "INSUFFICIENT_EVIDENCE"; print("NEG-011 OK")
assert run(build(orc={"examined_artifacts": [{"path": "outro.py", "sha256": "a"*64, "bytes_read": 1}]})) in ("FAIL", "INSUFFICIENT_EVIDENCE"); print("NEG-012 OK")
assert run(build(orc={"examined_artifacts": [{"path": "../fora.py", "sha256": "a"*64, "bytes_read": 1}]})) == "FAIL"; print("NEG-013a OK")
assert run(build(orc={"examined_artifacts": [{"path": "/etc/passwd", "sha256": "a"*64, "bytes_read": 1}]})) == "FAIL"; print("NEG-013b OK")
def mk(tmp):
    o = os.path.join(tempfile.gettempdir(), "fora_e5.txt"); open(o, "w").write("fora"); os.symlink(o, os.path.join(tmp, "link.py"))
assert run(build(orc={"examined_artifacts": [{"path": "link.py", "sha256": "a"*64, "bytes_read": 4}]}), files=mk) == "FAIL"; print("NEG-013c OK")
assert run(build(), keys={KEY_ID: {"public_key_bytes": b"x"*31, "fingerprint": "x", "authorized_for": ["E5"], "revoked": False}}) == "FAIL"; print("NEG-014 OK")
assert run(build(orc={"signature": "zz"*64})) == "FAIL"; print("NEG-015 OK")
assert run(build(), keys={KEY_ID: {"public_key_bytes": pub_bytes, "fingerprint": key_fingerprint(pub_bytes), "authorized_for": ["E5"], "revoked": True}}) == "FAIL"; print("NEG-017 OK")
assert run(build(), keys={KEY_ID: {"public_key_bytes": pub_bytes, "fingerprint": key_fingerprint(pub_bytes), "authorized_for": ["E6"], "revoked": False}}) == "FAIL"; print("NEG-018 OK")
print("SUITE v1.1.6.3 COMPLETA")



E5 v1.1.6.3 - verifier + suite

