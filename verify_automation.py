import json
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

# SÓ VERIFICA - nunca gera ou carrega chave privada
reg = json.loads(Path("keys/key-e6-01.json").read_text())
pub = Ed25519PublicKey.from_public_bytes(bytes.fromhex(reg["public_key_hex"]))
assert not list(Path(".").rglob("minha_chave_privada.pem"))
assert not list(Path(".").rglob("private.key"))
print("Verification passed - verify_automation (verify-only)")
print("public key OK:", reg["public_key_hex"][:16] + "...")
