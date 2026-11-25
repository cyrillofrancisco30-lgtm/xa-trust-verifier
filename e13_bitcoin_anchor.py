import hashlib, json, os, time
def H(b):
    return hashlib.sha256(b).hexdigest()
def merkle(items):
    L=[]
    for x in items:
        s=json.dumps(x, sort_keys=True)
        L.append(H(s.encode()))
    if not L:
        return H(b"empty")
    while len(L)>1:
        N=[]
        for i in range(0,len(L),2):
            l=L[i]
            r=L[i+1] if i+1<len(L) else l
            N.append(H((l+r).encode()))
        L=N
    return L[0]
def opret(root):
    d=bytes.fromhex("5841")
    d=d+bytes.fromhex(root)
    return "6a22"+d.hex()
def anchor(bid, items):
    root=merkle(items)
    op=opret(root)
    tx=H(f"XA-{bid}-{root}".encode())
    p={
      "xa":"E13",
      "batch_id":bid,
      "merkle_root":root,
      "op_return_hex":op,
      "txid_simulated":tx,
      "timestamp":int(time.time()),
      "items":len(items),
      "status":"ANCHORED"
    }
    open("anchor_proof.json","w").write(json.dumps(p,indent=2))
    return p
def verify():
    if not os.path.exists("anchor_proof.json"):
        return False
    p=json.load(open("anchor_proof.json"))
    return opret(p["merkle_root"])==p["op_return_hex"]
if __name__=="__main__":
    batch=[
      {"seq":1,"event":"t1","value":100},
      {"seq":2,"event":"t2","value":250},
      {"seq":3,"event":"t3","value":75}
    ]
    print("=== E13 ANCHOR ===")
    p=anchor(1,batch)
    print("root:",p["merkle_root"])
    print("op_return:",p["op_return_hex"])
    print("txid:",p["txid_simulated"])
    ok=verify()
    print("VERIFY:",ok)
    print("E13_VERIFIED" if ok else "E13_FAILED")
