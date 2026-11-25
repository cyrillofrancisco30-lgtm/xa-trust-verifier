from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
import hashlib, json, os

os.makedirs("keys", exist_ok=True)
sk = Ed25519PrivateKey.generate()
vk = sk.public_key()

priv_hex = sk.private_bytes(serialization.Encoding.Raw, serialization.PrivateFormat.Raw, serialization.NoEncryption()).hex()
pub_hex = vk.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw).hex()
fingerprint = hashlib.sha256(bytes.fromhex(pub_hex)).hexdigest()

open("keys/private.key","w").write(priv_hex)
open("keys/public.key","w").write(pub_hex)
open("keys/public.json","w").write(json.dumps({
  "alg": "Ed25519",
  "public_key_hex": pub_hex,
  "fingerprint_sha256": fingerprint,
  "key_id": fingerprint[:16]
}, indent=2))

print("PUB:", pub_hex)
print("FINGERPRINT:", fingerprint)
print("KEY_ID:", fingerprint[:16])
