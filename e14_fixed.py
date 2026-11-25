import hashlib
import json
import os
import time
import urllib.request

def H(b):
    return hashlib.sha256(b).hexdigest()

def merkle(items):
    L = []
    for x in items:
        s = json.dumps(x, sort_keys=True)
        s = s.replace(" ", "")
        L.append(H(s.encode()))
    if not L:
        return H(b"empty")
    while len(L) > 1:
        N = []
        for i in range(0, len(L), 2):
            l = L[i]
            r = l
            if i + 1 < len(L):
                r = L[i+1]
            N.append(H((l+r).encode()))
        L = N
    return L[0]

def opret(root):
    d = "5841" + root
    return "6a22" + d

def check(txid, expected_op):
    u = "https://mempool.space/testnet/api/tx/" + txid
    try:
        q = urllib.request.Request(u)
        q.add_header("User-Agent", "XA")
        with urllib.request.urlopen(q) as r:
            info = json.loads(r.read())
    except Exception as e:
        return {"error": str(e)}

    # 1. Tem que estar confirmada
    status = info.get("status", {})
    if not status.get("confirmed"):
        return {"verdict": "REJECTED", "reason": "tx nao confirmada", "txid": txid}

    # 2. Tem que ter um output OP_RETURN igual ao calculado
    found = False
    for out in info.get("vout", []):
        script = out.get("scriptpubkey", "")
        if script == expected_op:
            found = True
            break

    if not found:
        return {"verdict": "REJECTED", "reason": "OP_RETURN nao bate com o root calculado", "txid": txid}

    return {
        "verdict": "VERIFIED",
        "txid": txid,
        "block_height": status.get("block_height"),
        "block_time": status.get("block_time"),
        "op_return": expected_op,
    }

b1 = {"seq": 1, "event": "t1", "value": 100}
b2 = {"seq": 2, "event": "t2", "value": 250}
b3 = {"seq": 3, "event": "t3", "value": 75}
batch = [b1, b2, b3]
root = merkle(batch)
op = opret(root)

print("=== E14 FIXED ANCHOR ===")
print("root:", root)
print("op_return:", op)

txid = os.environ.get("XA_TXID", "")
if not txid:
    p = {
        "xa": "E14",
        "merkle_root": root,
        "op_return_hex": op,
        "status": "PENDING_ONCHAIN",
        "timestamp": int(time.time())
    }
    open("anchor_real_proof.json", "w").write(json.dumps(p))
    print("status: PENDING_ONCHAIN")
    print("E14_PENDING")
else:
    result = check(txid, op)
    print(json.dumps(result, indent=2))
    if result.get("verdict") == "VERIFIED":
        print("E14_VERIFIED")
    else:
        print("E14_REJECTED")
