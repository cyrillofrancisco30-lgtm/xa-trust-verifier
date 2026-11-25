import sys, json, hashlib
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

sig_file = sys.argv[1]
sig_data = json.load(open(sig_file))
path = sig_data["file"]
data = open(path, "rb").read()

# 1. confere o hash
assert hashlib.sha256(data).hexdigest() == sig_data["sha256"], "HASH DIVERGENTE!"
# 2. confere a assinatura
vk = Ed25519PublicKey.from_public_bytes(bytes.fromhex(sig_data["public_key_hex"]))
vk.verify(bytes.fromhex(sig_data["signature_hex"]), data)
print(f"✅ VÁLIDO: {path} | key_id {sig_data['key_id']}")
