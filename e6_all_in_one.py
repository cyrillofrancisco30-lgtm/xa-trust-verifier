# XA-TRUST E6 v1.1.6.4 - TUDO EM 1 ARQUIVO
# E6 = E5 + lote + anti-replay + expiracao + revogacao em lote
# pip install rfc8785==0.1.2 cryptography==42.0.5
# python e6_all_in_one.py
import hashlib, re, os, tempfile, json, time
import rfc8785
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

HEX64 = re.compile(r"^[0-9a-f]{64}$")
HEX128 = re.compile(r"^[0-9a-f]{128}$")

def fp(b):
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
    if receipt.get("fingerprint") != fp(pub): return "FAIL"
    if "E5" not in key.get("authorized_for", []) and "E6" not in key.get("authorized_for", []): return "FAIL"
    if key.get("revoked"): return "FAIL"
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

# --- E6: camada lote ---
def verify_e6_batch(receipts, claims_by_id, keys, manifests, read_fn, root, now=None):
    if now is None: now = int(time.time())
    if not isinstance(receipts, list) or len(receipts) == 0: return "INSUFFICIENT_EVIDENCE"
    if len(receipts) > 100: return "FAIL"
    seen_ids = set()
    seen_sigs = set()
    for r in receipts:
        # anti-replay: claim_id + signature unicos
        cid = r.get("claim_id")
        sig = r.get("signature", "")
        if not cid or cid in seen_ids: return "FAIL"
        seen_ids.add(cid)
        if sig in seen_sigs: return "FAIL"
        seen_sigs.add(sig)
        # expiracao: payload deve ter exp > now
        pay = r.get("signed_payload") or {}
        exp = pay.get("exp")
        if type(exp) is not int: return "FAIL"
        if exp <= now: return "FAIL"
        if exp > now + 86400*365: return "FAIL"
        # claim deve existir
        claim = claims_by_id.get(cid)
        if not claim: return "NOT_VERIFIED"
        mb = manifests.get(cid)
        res = verify_e5(r, claim, keys, mb, read_fn, root)
        if res != "PASS": return res
    return "PASS"

# --- Setup teste ---
priv = Ed25519PrivateKey.generate()
pub_bytes = priv.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
KEY_ID = "key-e6-test-01"
KEYS = {KEY_ID: {"public_key_bytes": pub_bytes, "fingerprint": fp(pub_bytes), "authorized_for": ["E5", "E6"], "revoked": False}}
NOW = 1800000000

def make_receipt(cid, scope, exp_offset=3600, tamper=None):
    mart = [{"path": "src/runtime/execution.py", "sha256": hashlib.sha256(b"print(1)\n").hexdigest()}]
    mb = rfc8785.dumps({"artifacts": mart})
    if isinstance(mb, str): mb = mb.encode()
    mh = hashlib.sha256(mb).hexdigest()
    pay = {"claim_id": cid, "claim_scope": scope, "manifest_sha256": mh, "exp": NOW + exp_offset}
    if tamper: pay.update(tamper)
    canon = rfc8785.dumps(pay)
    if isinstance(canon, str): canon = canon.encode()
    r = {"claim_id": cid, "claim_scope": scope, "public_key_id": KEY_ID, "fingerprint": fp(pub_bytes), "signed_payload_sha256": hashlib.sha256(canon).hexdigest(), "signed_payload": pay, "signature": priv.sign(canon).hex(), "manifest_sha256": mh, "examined_artifacts": [{"path": "src/runtime/execution.py", "sha256": mart[0]["sha256"], "bytes_read": 9}]}
    return r, mb

def run_batch(receipts, claims, manifests, keys=None):
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "src/runtime"), exist_ok=True)
        open(os.path.join(tmp, "src/runtime/execution.py"), "wb").write(b"print(1)\n")
        def read_fn(p):
            with open(os.path.realpath(os.path.join(tmp, p)), "rb") as fh: return fh.read()
        return verify_e6_batch(receipts, claims, keys or KEYS, manifests, read_fn, tmp, now=NOW)

S1 = {"repository": "github.com/xa-finance/core", "workflow": "verify", "commit_sha": "c9eb1f2f"}
S2 = {"repository": "github.com/xa-finance/core", "workflow": "verify", "commit_sha": "a1b2c3d4"}
r1, mb1 = make_receipt("CLM-001", S1)
r2, mb2 = make_receipt("CLM-002", S2)
claims = {"CLM-001": {"claim_id": "CLM-001", "claim_scope": S1}, "CLM-002": {"claim_id": "CLM-002", "claim_scope": S2}}
mans = {"CLM-001": mb1, "CLM-002": mb2}

assert run_batch([r1, r2], claims, mans) == "PASS"; print("POS-E6-001 PASS lote 2 OK")
assert run_batch([r1, r1], claims, mans) == "FAIL"; print("NEG-E6-001 OK replay claim_id duplicado")
r_dup_sig, _ = make_receipt("CLM-003", S1)
r_dup_sig["signature"] = r1["signature"]
claims3 = dict(claims); claims3["CLM-003"] = {"claim_id": "CLM-003", "claim_scope": S1}
mans3 = dict(mans); mans3["CLM-003"] = mb1
# assinatura duplicada mas payload diferente -> E5 ja falha, E6 tambem falha
assert run_batch([r1, r_dup_sig], claims3, mans3) == "FAIL"; print("NEG-E6-002 OK assinatura duplicada")
r_exp, mb_exp = make_receipt("CLM-004", S1, exp_offset=-10)
claims4 = dict(claims); claims4["CLM-004"] = {"claim_id": "CLM-004", "claim_scope": S1}
mans4 = dict(mans); mans4["CLM-004"] = mb_exp
assert run_batch([r_exp], claims4, mans4) == "FAIL"; print("NEG-E6-003 OK expirado")
r_noexp, mb_noexp = make_receipt("CLM-005", S1)
del r_noexp["signed_payload"]["exp"]
# re-assina sem exp para teste valido de falta de exp
pay = r_noexp["signed_payload"]; canon = rfc8785.dumps(pay)
if isinstance(canon, str): canon = canon.encode()
r_noexp["signature"] = priv.sign(canon).hex(); r_noexp["signed_payload_sha256"] = hashlib.sha256(canon).hexdigest()
claims5 = dict(claims); claims5["CLM-005"] = {"claim_id": "CLM-005", "claim_scope": S1}
mans5 = dict(mans); mans5["CLM-005"] = mb_noexp
assert run_batch([r_noexp], claims5, mans5) == "FAIL"; print("NEG-E6-004 OK sem exp")
assert run_batch([], claims, mans) == "INSUFFICIENT_EVIDENCE"; print("NEG-E6-005 OK lote vazio")
r_rev, mb_rev = make_receipt("CLM-006", S1)
claims6 = dict(claims); claims6["CLM-006"] = {"claim_id": "CLM-006", "claim_scope": S1}
mans6 = dict(mans); mans6["CLM-006"] = mb_rev
keys_rev = {KEY_ID: {"public_key_bytes": pub_bytes, "fingerprint": fp(pub_bytes), "authorized_for": ["E5", "E6"], "revoked": True}}
assert run_batch([r_rev], claims6, mans6, keys=keys_rev) == "FAIL"; print("NEG-E6-006 OK chave revogada")
assert run_batch([r1], {"CLM-999": {"claim_id": "CLM-999", "claim_scope": S1}}, mans) == "NOT_VERIFIED"; print("NEG-E6-007 OK claim desconhecido")
print("SUITE v1.1.6.4 COMPLETA")