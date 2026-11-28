import segno, hashlib, json, datetime, sys
from pathlib import Path

arquivo = sys.argv[1] if len(sys.argv) > 1 else "doc1.txt"
dados = Path(arquivo).read_bytes()
h = hashlib.sha256(dados).hexdigest()
link = f"https://cyrillofrancisco30-lgtm.github.io/xa-trust-verifier/verificar.html#{h}"

qr = segno.make(link)
qr.save(f"selo_{Path(arquivo).stem}.png", scale=10, border=2)

recibo = {
  "arquivo": arquivo,
  "sha256": h,
  "link_verificacao": link,
  "data": datetime.datetime.now().isoformat(),
  "instrucao": "Escaneie o QR para verificar"
}
Path(f"selo_{Path(arquivo).stem}.json").write_text(json.dumps(recibo, indent=2))
print("✅ SELO CRIADO")
print("QR:", f"selo_{Path(arquivo).stem}.png")
print("Hash:", h[:16] + "...")
print("Link:", link)
