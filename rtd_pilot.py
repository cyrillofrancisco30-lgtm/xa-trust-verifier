import hashlib, json, os
from datetime import date

ARQUIVO = "documentos_dia.json"

def sha256_arquivo(caminho):
    with open(caminho, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

def add_document(caminho_pdf):
    h = sha256_arquivo(caminho_pdf)
    docs = []
    if os.path.exists(ARQUIVO):
        docs = json.load(open(ARQUIVO))
    docs.append({"arquivo": caminho_pdf, "hash": h, "data": str(date.today())})
    json.dump(docs, open(ARQUIVO, 'w'), indent=2)
    print(f"OK adicionado: {h[:16]}...")
    print(f"Total hoje: {len(docs)}")
    return h

def merkle_root(hashes):
    if not hashes:
        return None
    nivel = hashes[:]
    while len(nivel) > 1:
        prox = []
        for i in range(0, len(nivel), 2):
            a = nivel[i]
            b = nivel[i+1] if i+1 < len(nivel) else a
            prox.append(hashlib.sha256((a+b).encode()).hexdigest())
        nivel = prox
    return nivel[0]

def close_day():
    if not os.path.exists(ARQUIVO):
        print("Nenhum documento hoje.")
        return
    docs = json.load(open(ARQUIVO))
    hashes = [d["hash"] for d in docs]
    root = merkle_root(hashes)
    prova = {
        "cartorio": "PILOTO RTD",
        "data": str(date.today()),
        "qtd": len(docs),
        "merkle_root": root,
        "documentos": docs,
        "status": "pronto para tx OP_RETURN"
    }
    json.dump(prova, open("publish_proof.json", 'w'), indent=2)
    print(f"--- FECHAMENTO DO DIA ---")
    print(f"Documentos: {len(docs)}")
    print(f"Merkle Root: {root}")
    print(f"Salvo em: publish_proof.json")
    print(f"Proximo passo: 1 tx com OP_RETURN = {root[:32]}...")

if __name__ == "__main__":
    print("E18 Piloto Cartorio pronto!")
    print("Comandos: add_document() / close_day()")
