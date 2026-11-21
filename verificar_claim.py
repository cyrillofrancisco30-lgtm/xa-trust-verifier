import json, hashlib, base64
import rfc8785
from cryptography.hazmat.primitives import serialization

s = json.load(open("claim.json"))
c = rfc8785.dumps(s["claim"])
print("1. JCS canonical bate?", c.decode() == s["canonical"])
print("2. SHA-256 bate?", hashlib.sha256(c).hexdigest() == s["canonical_sha256"])
try:
    pub = serialization.load_pem_public_key(s["public_key_pem"].encode())
    pub.verify(base64.b64decode(s["signature_b64"]), c)
    print("3. Ed25519 assinatura VALIDA? True")
    print("\nRESULTADO: VERIFIED")
except Exception as e:
    print("3. Ed25519 assinatura VALIDA? False", e)
    print("\nRESULTADO: FAIL")
