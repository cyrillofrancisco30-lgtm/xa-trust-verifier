import json, hashlib, pathlib
from cryptography.hazmat.primitives.serialization import load_pem_private_key
HOME = pathlib.Path.home()
priv = load_pem_private_key((HOME / ".xa-trust-keys" / "e6-key-01.priv.pem").read_bytes(), None)
reg = json.loads(pathlib.Path("keys/key-e6-01.json").read_text())
def canon(o): return json.dumps(o, sort_keys=True, separators=(",", ":")).encode()
receipt = {"claim": "claim-e6-real-001", "manifest": "manifest-e6-001", "scope": "E6", "key_id": reg["key_id"], "fingerprint": reg["fingerprint"], "commit": "c325e7a"}
receipt["signature_hex"] = priv.sign(canon(receipt)).hex()
pathlib.Path("artifacts").mkdir(exist_ok=True)
pathlib.Path("artifacts/e6-receipt-001.json").write_text(json.dumps(receipt, indent=2) + "\n")
print("RECEIPT SALVO artifacts/e6-receipt-001.json")
print("signature:", receipt["signature_hex"][:32] + "...")
print("sha256:", hashlib.sha256(pathlib.Path("artifacts/e6-receipt-001.json").read_bytes()).hexdigest())
