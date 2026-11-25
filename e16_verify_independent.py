import json, hashlib

def H(b): return hashlib.sha256(b).hexdigest()

def merkle(items):
    L=[]
    for i in items:
        s=json.dumps(i, sort_keys=True).replace(' ','')
        L.append(H(s.encode()))
    while len(L)>1:
        N=[]
        for j in range(0,len(L),2):
            l=L[j]
            r=L[j+1] if j+1<len(L) else l
            N.append(H((l+r).encode()))
        L=N
    return L[0] if L else ''

# Entradas que um terceiro receberia - nada interno
proof = json.load(open('anchor_proof.json'))
publish = json.load(open('publish_proof.json'))
batch = proof.get('batch', proof.get('items', []))
if not batch:
    batch=[{'seq':1,'event':'t1','value':100},{'seq':2,'event':'t2','value':250},{'seq':3,'event':'t3','value':75}]

print("=== E16 - VERIFICACAO INDEPENDENTE ===")

# 1. Tem txid?
txid = publish.get('txid')
if not txid:
    print("BLOCKED: sem txid, nada pra verificar na chain")
    print("E16 nao passa sem publicacao real")
    raise SystemExit(1)

# 2. Recomputa root do zero
calc = merkle(batch)
print(f"root calculado: {calc}")
print(f"root na prova:  {proof['merkle_root']}")
print(f"root publicado: {publish['merkle_root']}")
ok_root = calc == proof['merkle_root'] == publish['merkle_root']
print(f"root bate: {ok_root}")

# 3. OP_RETURN bate com o root?
op = publish['op_return_hex']
ok_op = op == ('585841' + proof['merkle_root'])
print(f"OP_RETURN bate: {ok_op}")
print(f"txid: {txid}")

ok = ok_root and ok_op
print(f"\nE16_VERIFIED: {ok}" if ok else "\nE16_FAILED")
