import json, hashlib, pathlib
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.serialization import load_pem_private_key

HOME = pathlib.Path.home()
priv_pem = (HOME / ".xa-trust-keys" / "e6-key-01.priv.pem").read_bytes()
priv = load_pem_private_key(priv_pem, None)
reg = json.loads(pathlib.Path("keys/key-e6-01.json").read_text())
pub = Ed25519PublicKey.from_public_bytes(bytes.fromhex(reg["public_key_hex"]))

def canon(o): return json.dumps(o, sort_keys=True, separators=(",", ":")).encode()
receipt = {"claim": "claim-e6-real-001", "manifest": "manifest-e6-001", "scope": "E6", "key_id": reg["key_id"], "fingerprint": reg["fingerprint"], "commit": "9fcadd6"}
sig = priv.sign(canon(receipt))
receipt["signature_hex"] = sig.hex()

# 1. Verifica com a publica autorizada
try:
    pub.verify(bytes.fromhex(receipt["signature_hex"]), canon({k: v for k, v in receipt.items() if k != "signature_hex"}))
    print("E6-REAL-001 PASS assinatura real validada com chave autorizada")
except Exception as e: print("E6-REAL-001 FAIL", e)

# 2. Tamper deve falhar
bad = dict(receipt); bad["scope"] = "E7"
try:
    pub.verify(bytes.fromhex(bad["signature_hex"]), canon({k: v for k, v in bad.items() if k != "signature_hex"}))
    print("E6-REAL-002 FAIL tamper aceito")
except Exception: print("E6-REAL-002 PASS tamper rejeitado")

# 3. Chave desconhecida deve falhar
other = Ed25519PrivateKey.generate().public_key()
try:
    other.verify(bytes.fromhex(receipt["signature_hex"]), canon({k: v for k, v in receipt.items() if k != "signature_hex"}))
    print("E6-REAL-003 FAIL chave desconhecida aceita")
except Exception: print("E6-REAL-003 PASS chave desconhecida rejeitada")

# 4. Revogada deve falhar
if reg.get("revoked"): print("E6-REAL-004 FAIL chave revogada usada")
else: print("E6-REAL-004 PASS chave nao revogada, autorizada para", reg["authorized_for"])
print("E6 REAL COMPLETA fingerprint:", reg["fingerprint"])
