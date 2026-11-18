import json
import base64
import rfc8785
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

KEY_FILE = Path("minha_chave_privada.pem")

if KEY_FILE.exists():
    private_key = serialization.load_pem_private_key(KEY_FILE.read_bytes(), password=None)
else:
    private_key = Ed25519PrivateKey.generate()
    KEY_FILE.write_bytes(private_key.private_bytes(encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.PKCS8, encryption_algorithm=serialization.NoEncryption()))
    print("Nova chave privada criada! Guarde ela, nao compartilhe!")

public_key = private_key.public_key()

payload = {
    "autor": "Cyrillo Francisco",
    "projeto": "xa-trust-verifier",
    "mensagem": "Eu sou o autor original deste projeto",
    "data": "2026-11-18"
}

canonical_bytes = rfc8785.dumps(payload)
signature = private_key.sign(canonical_bytes)

try:
    public_key.verify(signature, canonical_bytes)
    print("Verification passed - evidence.json created")
except Exception:
    print("Verification FAILED")
    raise SystemExit(1)

public_pem = public_key.public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo).decode()

evidence = {
    "payload": payload,
    "canonical_bytes": canonical_bytes.decode(),
    "signature": base64.b64encode(signature).decode(),
    "public_key": public_pem
}

Path("evidence.json").write_text(json.dumps(evidence, indent=2))
print("Assinatura salva em evidence.json")