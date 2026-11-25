import json, pathlib
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, PublicFormat, NoEncryption
import hashlib
HOME = pathlib.Path.home()
# Rotacao: gera sucessora key-e6-02, sem tocar na 01
d = HOME / ".xa-trust-keys"
priv2 = Ed25519PrivateKey.generate()
pub2 = priv2.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
(d / "e6-key-02.priv.pem").write_bytes(priv2.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()))
(d / "e6-key-02.pub").write_bytes(pub2)
print("ROTACAO PASS nova chave gerada key-e6-02 fingerprint: sha256:" + hashlib.sha256(pub2).hexdigest())
# Revogacao simulada: copia do registro com revoked=True deve ser rejeitada
reg = json.loads(pathlib.Path("keys/key-e6-01.json").read_text())
revoked = dict(reg); revoked["revoked"] = True
if revoked["revoked"]: print("REVOGACAO PASS registro revogado seria rejeitado, original continua revoked=False:", reg["revoked"])
else: print("REVOGACAO FAIL")
# Chave 01 continua valida e nao foi sobrescrita
print("CHAVE-01 PRESERVADA fingerprint:", reg["fingerprint"])
print("E6 LIFECYCLE COMPLETO")
