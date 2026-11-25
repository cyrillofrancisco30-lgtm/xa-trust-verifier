"""
E11 - Merkle Proof Individual
REGRA CRITICA: leaf = SHA256(b"\x00" + canonical_serialize(event))
NAO MUDAR - senao quebra E3/E4/E10
"""
import hashlib
import json

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def canonical_serialize(payload) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()

def leaf_hash(item) -> str:
    # REGRA CRITICA - igual E3/E4/E10
    return sha256(b"\x00" + canonical_serialize(item))

def rebuild_merkle_root(items) -> str:
    if not items:
        return ""
    layer = [leaf_hash(i) for i in items]
    while len(layer) > 1:
        if len(layer) % 2 == 1:
            layer.append(layer[-1])
        nxt = []
        for i in range(0, len(layer), 2):
            nxt.append(sha256((layer[i] + layer[i+1]).encode()))
        layer = nxt
    return layer[0]

def generate_merkle_proof(items, target_index):
    if target_index >= len(items):
        raise Exception("index out of range")
    layer = [leaf_hash(i) for i in items]
    index = target_index
    proof = []
    while len(layer) > 1:
        if len(layer) % 2 == 1:
            layer.append(layer[-1])
        sibling_index = index ^ 1
        proof.append({
            "position": "right" if index % 2 == 0 else "left",
            "hash": layer[sibling_index]
        })
        nxt = []
        for i in range(0, len(layer), 2):
            nxt.append(sha256((layer[i] + layer[i+1]).encode()))
        index //= 2
        layer = nxt
    return proof, layer[0]

def verify_merkle_proof(event, proof, expected_root) -> bool:
    current = sha256(b"\x00" + canonical_serialize(event))
    for step in proof:
        if step["position"] == "right":
            combined = (current + step["hash"]).encode()
        else:
            combined = (step["hash"] + current).encode()
        current = sha256(combined)
    return current == expected_root

if __name__ == "__main__":
    # Teste deterministico
    items = [
        {"id": 1, "value": 100},
        {"id": 2, "value": 200},
        {"id": 3, "value": 300},
        {"id": 4, "value": 400},
        {"id": 5, "value": 500},
    ]
    root = rebuild_merkle_root(items)
    print(f"MERKLE_ROOT: {root}")

    for idx in range(len(items)):
        proof, r2 = generate_merkle_proof(items, idx)
        assert r2 == root, "root divergente"
        ok = verify_merkle_proof(items[idx], proof, root)
        print(f"index={idx} proof_len={len(proof)} VERIFIED={ok}")
        assert ok, f"falhou index {idx}"

    # Teste negativo: evento adulterado deve FALHAR
    proof, _ = generate_merkle_proof(items, 0)
    tampered = {"id": 1, "value": 999}
    ok_bad = verify_merkle_proof(tampered, proof, root)
    print(f"tampered VERIFIED={ok_bad} (tem que ser False)")
    assert ok_bad == False

    print("E11_VERIFIED")
