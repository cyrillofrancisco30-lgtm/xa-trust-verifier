

import json, sys, time, hashlib, base64
from pathlib import Path
import rfc8785
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.exceptions import InvalidSignature

def fail(m):
    print(f"REJECTED: {m}")
    sys.exit(1)

if len(sys.argv) < 2:
    print("Uso: python3 verify_independent.py claim.json")
    sys.exit(1)

p = Path(sys.argv[1])
env = json.loads(p.read_text(encoding="utf-8"))

claim = env.get("claim")
sig_b64 = env.get("signature_b64")
pk_pem = env.get("public_key_pem")
canonical_guardado = env.get("canonical")
hash_guardado = env.get("canonical_sha256")
proof = env.get("proof_type")

if not isinstance(claim, dict):
    fail("campo 'claim' ausente")
if not sig_b64 or not pk_pem:
    fail("signature_b64 ou public_key_pem ausente")
if proof != "Ed25519+JCS-RFC8785":
    fail(f"proof_type inesperado: {proof}")

# 1. Recalcula o canonico pela RFC 8785, nao confia no que veio
try:
    canonical = rfc8785.dumps(claim)
except Exception as e:
    fail(f"falha RFC 8785: {e}")

# 2. Compara com o canonico guardado
if canonical_guardado and canonical.decode() != canonical_guardado:
    fail("canonical guardado != canonical RFC 8785 recalculado")

# 3. Compara o hash
h = hashlib.sha256(canonical).hexdigest()
if hash_guardado and h != hash_guardado:
    fail("canonical_sha256 nao bate")

# 4. Verifica assinatura Ed25519 de verdade
try:
    pub = load_pem_public_key(pk_pem.encode())
    sig = base64.b64decode(sig_b64)
    pub.verify(sig, canonical)
except InvalidSignature:
    fail("assinatura Ed25519 invalida")
except Exception as e:
    fail(f"erro Ed25519: {e}")

print("VERIFIED")
print(f"proof_type: {proof}")
print(f"hash_claim_canonico: {h}")
print(f"verificado_em: {int(time.time())}")
print("motivo: canonical RFC8785 + hash + assinatura Ed25519 OK")


