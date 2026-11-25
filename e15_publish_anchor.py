import json, hashlib

def H(b): return hashlib.sha256(b).hexdigest()

proof = json.load(open('anchor_proof.json'))
root = proof['merkle_root']

# OP_RETURN: XA + root (32 bytes)
op_return = bytes.fromhex('585841') + bytes.fromhex(root)
print(f"root: {root}")
print(f"OP_RETURN ({len(op_return)} bytes): {op_return.hex()}")
print(f"OP_RETURN asm: OP_RETURN {op_return.hex()}")

# Ainda sem broadcast real - prepara o pacote pra publicar
publish = {
    "batch_id": proof['batch_id'],
    "merkle_root": root,
    "op_return_hex": op_return.hex(),
    "op_return_asm": f"OP_RETURN {op_return.hex()}",
    "status": "READY_TO_BROADCAST",
    "txid": None,
    "note": "Transmita esse OP_RETURN numa tx real e preencha o txid aqui"
}
json.dump(publish, open('publish_proof.json','w'), indent=2)
print("\nSalvo: publish_proof.json")
print("Status: READY_TO_BROADCAST")
print("Proximo passo: broadcast real -> preencher txid -> E16")
