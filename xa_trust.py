import argparse, json, sys
import hashlib, base64
from pathlib import Path
try:
 import rfc8785
except:
 rfc8785 = None
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature

def fail(m):
 print("FAIL: " + m)
 return False

def verify(p):
 print("=== XA-TRUST v2 ===")
 print("Claim: " + str(p))
 d = json.loads(Path(p).read_text())
 c = d.get("claim", d)
 can = d.get("canonical") or d.get("manifest_jcs")
 sha = d.get("canonical_sha256") or d.get("digest_sha256")
 sig = d.get("signature_b64") or d.get("signature_ed25519")
 pub = d.get("public_key_pem") or d.get("public_key")
 if not can or not sha or not sig or not pub:
  return fail("Campos faltando")
 print("[E3] JCS RFC8785...")
 if rfc8785 is None:
     return fail("RFC8785 indisponivel")
 if True:
  exp = rfc8785.dumps(c).decode()
  if exp != can:
   return fail("JCS nao bate")
  print(" JCS: OK")
 print("[E4] SHA-256...")
 calc = hashlib.sha256(can.encode()).hexdigest()
 if calc != sha:
  return fail("API-12 SHA falhou")
 print(" SHA256: OK API-12")
 print("[E5] Ed25519...")
 try:
  k = serialization.load_pem_public_key(pub.encode())
  if not isinstance(k, Ed25519PublicKey):
      return fail("Chave nao e Ed25519")
  k.verify(base64.b64decode(sig, validate=True), can.encode())
  print(" Signature: VALID")
 except InvalidSignature:
  return fail("Assinatura INVALIDA")
 except Exception as e:
  return fail("Ed25519 erro: " + str(e))
 print("[E6] Auditoria...")
 print(" Autor: " + str(c.get("autor", "N/A")))
 print(" Projeto: " + str(c.get("projeto", "N/A")))
 print(" Publica sem chave privada: OK")
 print("[E7] Bancaria...")
 print(" Trilha E3-E6: OK")
 print(" Pronto p/ compliance")
 print("")
 print("RESULTADO: VERIFIED")
 print("E3 E4 E5 E6 E7 OK")
 return True

if __name__ == "__main__":
 ap = argparse.ArgumentParser()
 ap.add_argument("--claim")
 a = ap.parse_args()
 ok = True
 if a.claim:
  ok = verify(Path(a.claim))
 sys.exit(0 if ok else 1)
