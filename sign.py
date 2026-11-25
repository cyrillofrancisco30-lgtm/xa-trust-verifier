import sys, json, hashlib
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

if len(sys.argv) < 2:
    print("uso: python3 sign.py arquivo.json")
    sys.exit(1)

path = sys.argv[1]
data = open(path, "rb").read()
priv_hex = open("keys/private.key").read().strip()
sk = Ed25519PrivateKey.from_private_bytes(bytes.fromhex(priv_hex))
sig = sk.sign(data)
pub_hex = open("keys/public.key").read().strip()

out = {
  "file": path,
  "sha256": hashlib.sha256(data).hexdigest(),
  "alg": "Ed25519",
  "key_id": hashlib.sha256(bytes.fromhex(pub_hex)).hexdigest()[:16],
  "public_key_hex": pub_hex,
  "signature_hex": sig.hex()
}
open(path + ".sig.json", "w").write(json.dumps(out, indent=2))
print("ASSINADO:", path)
print("SIG:", sig.hex()[:64] + "...")
print("Salvo em:", path + ".sig.json")
