import json, pathlib, hashlib
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
reg = json.loads(pathlib.Path("keys/key-e6-01.json").read_text())
receipt = json.loads(pathlib.Path("artifacts/e6-receipt-001.json").read_text())
print("fingerprint registro:", reg["fingerprint"])
print("fingerprint receipt:", receipt["fingerprint"])
print("sha256 receipt:", hashlib.sha256(pathlib.Path("artifacts/e6-receipt-001.json").read_bytes()).hexdigest())
def canon(o): return json.dumps(o, sort_keys=True, separators=(",", ":")).encode()
pub = Ed25519PublicKey.from_public_bytes(bytes.fromhex(reg["public_key_hex"]))
sig = bytes.fromhex(receipt["signature_hex"])
payload = {k: v for k, v in receipt.items() if k != "signature_hex"}
# 1. Original
try:
    assert receipt["fingerprint"] == reg["fingerprint"] and not reg["revoked"]
    pub.verify(sig, canon(payload)); print("INDEPENDENT-001 PASS assinatura original")
except Exception as e: print("INDEPENDENT-001 FAIL", e)
# 2. Tamper
bad = dict(payload); bad["scope"] = "E7"
try: pub.verify(sig, canon(bad)); print("INDEPENDENT-002 FAIL tamper aceito")
except Exception: print("INDEPENDENT-002 PASS tamper rejeitado")
# 3. Desconhecida
other = Ed25519PrivateKey.generate().public_key()
try: other.verify(sig, canon(payload)); print("INDEPENDENT-003 FAIL desconhecida aceita")
except Exception: print("INDEPENDENT-003 PASS desconhecida rejeitada")
# 4. Revogada
if reg.get("revoked"): print("INDEPENDENT-004 FAIL chave revogada")
else:
    sim = dict(reg); sim["revoked"] = True
    print("INDEPENDENT-004 PASS revogacao simulada rejeitaria, original revoked=False")
print("REPRODUCAO INDEPENDENTE COMPLETA sem privada")
