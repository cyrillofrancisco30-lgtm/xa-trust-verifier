# XA-TRUST E7 v1.1.6.5 - TUDO EM 1 ARQUIVO
# E7 = E5 + E6 + PROMOCAO / GOVERNANCA
# Regra: so promove se E5 PASS + E6 PASS + quorum + sem veto + janela valida
# pip install rfc8785==0.1.2  # cryptography: usar a ja instalada no Termux, 42.0.5 exige Rust
# python e7_all_in_one.py
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
    if not any(x in key.get("authorized_for", []) for x in ["E5", "E6", "E7"]): return "FAIL"
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

def verify_e6_batch(receipts, claims_by_id, keys, manifests, read_fn, root, now=None):
    if now is None: now = int(time.time())
    if not isinstance(receipts, list) or len(receipts) == 0: return "INSUFFICIENT_EVIDENCE"
    if len(receipts) > 100: return "FAIL"
    seen_ids = set(); seen_sigs = set()
    for r in receipts:
        cid = r.get("claim_id"); sig = r.get("signature", "")
        if not cid or cid in seen_ids: return "FAIL"
        seen_ids.add(cid)
        if sig in seen_sigs: return "FAIL"
        seen_sigs.add(sig)
        pay = r.get("signed_payload") or {}
        exp = pay.get("exp")
        if type(exp) is not int: return "FAIL"
        if exp <= now: return "FAIL"
        if exp > now + 86400*365: return "FAIL"
        claim = claims_by_id.get(cid)
        if not claim: return "NOT_VERIFIED"
        res = verify_e5(r, claim, keys, manifests.get(cid), read_fn, root)
        if res != "PASS": return res
    return "PASS"

# --- E7: promocao ---
def verify_e7_promotion(receipts, claims, keys, manifests, read_fn, root, approvals, vetoes=None, now=None, quorum=2, window_start=None, window_end=None):
    if now is None: now = int(time.time())
    if vetoes is None: vetoes = []
    # 1. janela de promocao
    if window_start is not None and now < window_start: return "NOT_PROMOTED"
    if window_end is not None and now > window_end: return "NOT_PROMOTED"
    # 2. veto bloqueia tudo
    if len(vetoes) > 0: return "NOT_PROMOTED"
    # 3. E5+E6 precisam passar
    res = verify_e6_batch(receipts, claims, keys, manifests, read_fn, root, now=now)
    if res != "PASS": return res
    # 4. quorum: aprovadores distintos, nao revogados, autorizados E7
    if not isinstance(approvals, list): return "FAIL"
    uniq = set()
    for a in approvals:
        kid = a.get("key_id")
        if not kid or kid in uniq: return "FAIL"
        uniq.add(kid)
        k = keys.get(kid)
        if not k: return "NOT_VERIFIED"
        if k.get("revoked"): return "FAIL"
        if "E7" not in k.get("authorized_for", []): return "FAIL"
        # assinatura da aprovacao deve ser valida sobre promotion_id
        pay = a.get("signed_payload") or {}
        if pay.get("promotion_id") != a.get("promotion_id"): return "FAIL"
        try:
            canon = rfc8785.dumps(pay)
            if isinstance(canon, str): canon = canon.encode()
        except Exception: return "FAIL"
        if a.get("signed_payload_sha256") != hashlib.sha256(canon).hexdigest(): return "FAIL"
        sig_hex = a.get("signature", "")
        if not HEX128.match(sig_hex): return "FAIL"
        try:
            Ed25519PublicKey.from_public_bytes(k["public_key_bytes"]).verify(bytes.fromhex(sig_hex), canon)
        except Exception: return "FAIL"
    if len(uniq) < quorum: return "NOT_PROMOTED"
    return "PROMOTED"

# --- Setup ---
NOW = 1800000000
priv1 = Ed25519PrivateKey.generate()
priv2 = Ed25519PrivateKey.generate()
priv3 = Ed25519PrivateKey.generate()
def pub_of(p): return p.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
P1, P2, P3 = pub_of(priv1), pub_of(priv2), pub_of(priv3)
KEYS = {
  "key-e7-01": {"public_key_bytes": P1, "fingerprint": fp(P1), "authorized_for": ["E5", "E6", "E7"], "revoked": False},
  "key-e7-02": {"public_key_bytes": P2, "fingerprint": fp(P2), "authorized_for": ["E5", "E6", "E7"], "revoked": False},
  "key-e7-03": {"public_key_bytes": P3, "fingerprint": fp(P3), "authorized_for": ["E5", "E6", "E7"], "revoked": False},
}
S1 = {"repository": "github.com/xa-finance/core", "workflow": "verify", "commit_sha": "cbd3911"}

def make_receipt(cid, scope):
    mart = [{"path": "src/runtime/execution.py", "sha256": hashlib.sha256(b"print(1)\n").hexdigest()}]
    mb = rfc8785.dumps({"artifacts": mart})
    if isinstance(mb, str): mb = mb.encode()
    mh = hashlib.sha256(mb).hexdigest()
    pay = {"claim_id": cid, "claim_scope": scope, "manifest_sha256": mh, "exp": NOW + 3600}
    canon = rfc8785.dumps(pay)
    if isinstance(canon, str): canon = canon.encode()
    r = {"claim_id": cid, "claim_scope": scope, "public_key_id": "key-e7-01", "fingerprint": fp(P1), "signed_payload_sha256": hashlib.sha256(canon).hexdigest(), "signed_payload": pay, "signature": priv1.sign(canon).hex(), "manifest_sha256": mh, "examined_artifacts": [{"path": "src/runtime/execution.py", "sha256": mart[0]["sha256"], "bytes_read": 9}]}
    return r, mb

def make_approval(priv, kid, promo="PROMO-001"):
    pay = {"promotion_id": promo, "action": "promote", "target": "CLM-001"}
    canon = rfc8785.dumps(pay)
    if isinstance(canon, str): canon = canon.encode()
    return {"promotion_id": promo, "key_id": kid, "signed_payload": pay, "signed_payload_sha256": hashlib.sha256(canon).hexdigest(), "signature": priv.sign(canon).hex()}

def run_promotion(receipts, claims, mans, approvals, vetoes=None, quorum=2, ws=None, we=None, keys=None):
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "src/runtime"), exist_ok=True)
        open(os.path.join(tmp, "src/runtime/execution.py"), "wb").write(b"print(1)\n")
        def read_fn(p):
            with open(os.path.realpath(os.path.join(tmp, p)), "rb") as fh: return fh.read()
        return verify_e7_promotion(receipts, claims, keys or KEYS, mans, read_fn, tmp, approvals, vetoes=vetoes, now=NOW, quorum=quorum, window_start=ws, window_end=we)

r1, mb1 = make_receipt("CLM-001", S1)
claims = {"CLM-001": {"claim_id": "CLM-001", "claim_scope": S1}}
mans = {"CLM-001": mb1}
ap2 = [make_approval(priv1, "key-e7-01"), make_approval(priv2, "key-e7-02")]

assert run_promotion([r1], claims, mans, ap2) == "PROMOTED"; print("POS-E7-001 PROMOTED quorum 2 OK")
assert run_promotion([r1], claims, mans, [make_approval(priv1, "key-e7-01")], quorum=2) == "NOT_PROMOTED"; print("NEG-E7-001 OK quorum insuficiente")
assert run_promotion([r1], claims, mans, ap2, vetoes=["veto-1"]) == "NOT_PROMOTED"; print("NEG-E7-002 OK veto bloqueia")
assert run_promotion([r1], claims, mans, ap2, ws=NOW+100) == "NOT_PROMOTED"; print("NEG-E7-003 OK fora da janela inicio")
assert run_promotion([r1], claims, mans, ap2, we=NOW-100) == "NOT_PROMOTED"; print("NEG-E7-004 OK fora da janela fim")
bad = make_approval(priv1, "key-e7-01"); bad["signature"] = "00"*64
assert run_promotion([r1], claims, mans, [bad, make_approval(priv2, "key-e7-02")]) == "FAIL"; print("NEG-E7-005 OK assinatura aprovacao invalida")
dup = [make_approval(priv1, "key-e7-01"), make_approval(priv1, "key-e7-01")]
assert run_promotion([r1], claims, mans, dup) == "FAIL"; print("NEG-E7-006 OK aprovador duplicado")
keys_rev = dict(KEYS); keys_rev["key-e7-02"] = {"public_key_bytes": P2, "fingerprint": fp(P2), "authorized_for": ["E5", "E6", "E7"], "revoked": True}
assert run_promotion([r1], claims, mans, ap2, keys=keys_rev) == "FAIL"; print("NEG-E7-007 OK aprovador revogado")
r_bad, mb_bad = make_receipt("CLM-001", S1); r_bad["signature"] = "00"*64
assert run_promotion([r_bad], claims, {"CLM-001": mb_bad}, ap2) == "FAIL"; print("NEG-E7-008 OK E5 falha bloqueia promocao")
print("SUITE v1.1.6.5 COMPLETA")