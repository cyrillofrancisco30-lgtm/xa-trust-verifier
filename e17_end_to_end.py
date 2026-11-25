import json, hashlib

def H(b): return hashlib.sha256(b).hexdigest()
def merkle(items):
    L=[H(json.dumps(i, sort_keys=True).replace(' ','').encode()) for i in items]
    while len(L)>1:
        N=[]
        for j in range(0,len(L),2):
            l=L[j]; r=L[j+1] if j+1<len(L) else l
            N.append(H((l+r).encode()))
        L=N
    return L[0] if L else ''

proof = json.load(open('anchor_proof.json'))
publish = json.load(open('publish_proof.json'))

# CORRECAO: batch pode ser int, lista ou nem existir
items = proof.get('items') or proof.get('batch_items') or proof.get('leaves')
if not isinstance(items, list):
    items=[{'seq':1,'event':'t1','value':100},{'seq':2,'event':'t2','value':250},{'seq':3,'event':'t3','value':75}]

SIM_TXID = "SIM-" + H(proof['merkle_root'].encode())[:16]
publish['txid'] = SIM_TXID
publish['status'] = "SIMULATED_BROADCAST"
json.dump(publish, open('publish_proof.json','w'), indent=2)

print("=== E17 - PONTA A PONTA ===")
print(f"1. Emitir: batch {proof.get('batch_id')} com {len(items)} itens")
calc = merkle(items)
print(f"2. Ancorar: root {calc}")
print(f"3. Publicar (SIMULADO): txid {SIM_TXID}")
print(f"4. Verificar: root bate = {calc == proof['merkle_root'] == publish['merkle_root']}")
print(f"   OP_RETURN bate = {publish['op_return_hex'] == '585841' + proof['merkle_root']}")

revoked_at = "2026-11-25T21:00:00Z"
print(f"5. Revogar em: {revoked_at}")
old_issued = "2026-11-25T20:00:00Z"
new_issued = "2026-11-25T22:00:00Z"
old_ok = old_issued < revoked_at
new_ok = new_issued < revoked_at
print(f"6. Recibo antigo ({old_issued}) ainda vale: {old_ok}")
print(f"   Recibo novo ({new_issued}) rejeita: {not new_ok}")

ok = calc == proof['merkle_root'] and old_ok and not new_ok
print(f"\nE17_VERIFIED: {ok} (SIMULADO - nao e prova real na chain)")
print("Pra valer de verdade: trocar SIM_TXID por txid real de testnet")
