"""
XA-TRUST - E13 Anchor / Merkle Evidence
Versao 2 - JCS / RFC8785 + Domain Separation + Verificacao Integral
Estado atual: E13_PREPARED + E13_LOCAL_VERIFIED
NAO e ancoragem blockchain comprovada sem txid real + confirmacao.
"""
import hashlib, json, os, sys

try:
    import rfc8785
    def canonical(item):
        return rfc8785.dumps(item)
except ImportError:
    # Fallback JCS-compativel: sort_keys + separators sem espaco
    def canonical(item):
        return json.dumps(item, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')

def leaf_hash(item):
    # 0x00 = folha. Domain separation.
    return hashlib.sha256(b"\x00" + canonical(item)).digest()

def node_hash(left: bytes, right: bytes):
    # 0x01 = no interno. Domain separation.
    return hashlib.sha256(b"\x01" + left + right).digest()

def merkle_root(items):
    if not items:
        return hashlib.sha256(b"\x00" + b"empty").hexdigest()
    level = [leaf_hash(it) for it in items]
    while len(level) > 1:
        nxt = []
        for i in range(0, len(level), 2):
            left = level[i]
            right = level[i+1] if i+1 < len(level) else level[i]  # duplica ultimo se impar
            nxt.append(node_hash(left, right))
        level = nxt
    return level[0].hex()

def opret(merkle_root_hex: str):
    # OP_RETURN: 6a + push + XA (58 41) + root (32 bytes)
    # 6a 22 5841 + root
    root = bytes.fromhex(merkle_root_hex)
    payload = b"\x58\x41" + root  # XA + root
    return (b"\x6a" + bytes([len(payload)]) + payload).hex()

def build(items, out="anchor_proof.json"):
    root = merkle_root(items)
    proof = {
        "format": "XA-TRUST-E13-v2",
        "canonicalization": "JCS-RFC8785",
        "merkle_version": 2,
        "domain_separation": {"leaf": "0x00", "node": "0x01"},
        "item_count": len(items),
        "merkle_root": root,
        "op_return_hex": opret(root),
        "op_return_asm": f"OP_RETURN XA {root}",
        "state": "E13_PREPARED",
        "anchored": False,
        "txid": None,
        "items": items,  # manifesto completo para reverificacao
    }
    json.dump(proof, open(out, "w"), indent=2, sort_keys=True)
    print(f"E13_PREPARED root={root} count={len(items)} op_return={proof['op_return_hex']}")
    return proof

def verify(path="anchor_proof.json"):
    if not os.path.exists(path):
        print("E13_FAIL: anchor_proof.json nao encontrado")
        return False
    p = json.load(open(path))
    # 1. Recalcula raiz a partir dos itens - NAO confia no JSON
    recalc_root = merkle_root(p.get("items", []))
    if recalc_root != p["merkle_root"]:
        print(f"E13_FAIL: merkle_root nao bate com itens. json={p['merkle_root']} recalc={recalc_root}")
        return False
    # 2. Confere contagem
    if len(p.get("items", [])) != p.get("item_count"):
        print("E13_FAIL: item_count nao bate")
        return False
    # 3. Confere OP_RETURN a partir da raiz recalculada
    if opret(recalc_root) != p["op_return_hex"]:
        print("E13_FAIL: op_return_hex nao bate com merkle_root")
        return False
    # 4. Se diz anchored, exige txid real
    if p.get("anchored") and not p.get("txid"):
        print("E13_FAIL: anchored=True sem txid")
        return False
    # 5. Se nao tem txid, e so local
    if not p.get("txid"):
        print(f"E13_LOCAL_VERIFIED root={recalc_root} count={p['item_count']} state=E13_LOCAL_VERIFIED (NAO ancorado em blockchain)")
        return True
    print(f"E13_ANCHORED root={recalc_root} txid={p['txid']} - aguardando confirmacao de bloco")
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "verify":
        sys.exit(0 if verify() else 1)
    # Demo: lote de 3 evidencias
    demo_items = [
        {"claim": "E14", "hash": "bd93dfeb...", "type": "anchor"},
        {"claim": "E15", "hash": "a1b2c3...", "type": "anchor"},
        {"claim": "E17", "hash": "d4e5f6...", "type": "e2e"},
    ]
    build(demo_items)
    verify()
