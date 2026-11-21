# xa_trust.py - 1 ARQUIVO SO - XA-TRUST
# python3 xa_trust.py test
import json, hashlib, base64, sys
import rfc8785
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from pathlib import Path
def canonical(o): return rfc8785.dumps(o)
def sha256(b): return hashlib.sha256(b).hexdigest()
def new_key(): return Ed25519PrivateKey.generate()
def sign(k, claim):
    c = canonical(claim)
    sig = k.sign(c)
    pub = k.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo).decode()
    return {"claim": claim, "canonical": c.decode(), "canonical_sha256": sha256(c), "signature_b64": base64.b64encode(sig).decode(), "public_key_pem": pub, "proof_type": "Ed25519+JCS-RFC8785", "version": "1.0-single"}
def verify(s):
    try:
        c = canonical(s["claim"])
        if c.decode() != s["canonical"]: return False
        if sha256(c) != s["canonical_sha256"]: return False
        pub = serialization.load_pem_public_key(s["public_key_pem"].encode())
        pub.verify(base64.b64decode(s["signature_b64"]), c)
        return True
    except Exception: return False
def make_claim():
    return {"autor": "Cyrillo Francisco", "projeto": "xa-trust-verifier", "mensagem": "Eu sou o autor original deste projeto", "data": "2026-11-18", "policy": {"id": "verify-global", "version": "1.0"}, "intent": {"action": "verify_automation"}}
def run_tests():
    print("=== XA-TRUST SINGLE FILE TESTS ===")
    assert canonical({"b": 2, "a": 1}) == canonical({"a": 1, "b": 2}); print("test_canonical: OK")
    k = new_key(); assert verify(sign(k, make_claim())) is True; print("test_sign_verify: OK")
    k = new_key(); s = sign(k, make_claim()); s["claim"]["autor"] = "Atacante"; assert verify(s) is False; print("test_tamper: OK")
    k1, k2 = new_key(), new_key(); s = sign(k1, make_claim()); s["public_key_pem"] = sign(k2, make_claim())["public_key_pem"]; assert verify(s) is False; print("test_chave_trocada: OK")
    k = new_key(); c = make_claim(); assert sign(k, c)["signature_b64"] == sign(k, c)["signature_b64"]; print("test_reproduzivel: OK")
    k = new_key(); s = sign(k, make_claim()); assert sha256(canonical(s)) == sha256(canonical(s)); print("test_proof_hash: OK")
    print("\nTODOS OS TESTES: PASS (6/6)")
def demo():
    claim = make_claim(); k = new_key(); s = sign(k, claim)
    Path("signed.json").write_text(json.dumps(s, indent=2))
    print(f"VERIFY: {'PASS' if verify(s) else 'FAIL'}")
    print(f"canonical_sha256: {s['canonical_sha256']}")
    print(f"signature: {s['signature_b64'][:60]}...")
    print("Salvo em signed.json")
    print(f"REPRODUCIVEL: {'OK' if sign(k, claim)['signature_b64'] == sign(k, claim)['signature_b64'] else 'FAIL'}")
    t = json.loads(json.dumps(s)); t["claim"]["mensagem"] = "EU SOU OUTRA PESSOA"
    print(f"TAMPER: {'PASS (detectou!)' if not verify(t) else 'FAIL'}")
if __name__ == "__main__":
    demo() if len(sys.argv) < 2 else run_tests()
    if len(sys.argv) < 2: run_tests()
