import hashlib, json, os
from datetime import date

def add_document(caminho_pdf):
    with open(caminho_pdf, 'rb') as f:
        h = hashlib.sha256(f.read()).hexdigest()
    print(f"Protocolo: {date.today()}-{h[:8]}")
    print(f"SHA256: {h}")
    return h

if __name__ == "__main__":
    print("E18 Piloto Cartorio pronto!")
