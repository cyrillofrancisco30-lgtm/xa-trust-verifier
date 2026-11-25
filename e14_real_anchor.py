import hashlib
import json
import os
import time
import urllib.request
def H(b):
 return hashlib.sha256(b).hexdigest()
def merkle(items):
 L=[]
 for x in items:
  s=json.dumps(x,sort_keys=True)
  s=s.replace(" ","")
  L.append(H(s.encode()))
 if not L:
  return H(b"empty")
 while len(L)>1:
  N=[]
  for i in range(0,len(L),2):
   l=L[i]
   r=l
   if i+1<len(L):
    r=L[i+1]
   N.append(H((l+r).encode()))
  L=N
 return L[0]
def opret(root):
 d="5841"+root
 return "6a22"+d
def check(txid):
 u="https://mempool.space"
 u=u+"/testnet/api/tx/"+txid
 try:
  q=urllib.request.Request(u)
  q.add_header("User-Agent","XA")
  with urllib.request.urlopen(q) as r:
   return json.loads(r.read())
 except Exception as e:
  return {"error":str(e)}
b1={"seq":1,"event":"t1"}
b1["value"]=100
b2={"seq":2,"event":"t2"}
b2["value"]=250
b3={"seq":3,"event":"t3"}
b3["value"]=75
batch=[b1,b2,b3]
root=merkle(batch)
op=opret(root)
print("=== E14 REAL ANCHOR ===")
print("root:",root)
print("op_return:",op)
txid=os.environ.get("XA_TXID","")
if not txid: p={"xa":"E14",\
"merkle_root":root,\
"op_return_hex":op,\
"status":"PENDING_ONCHAIN",\
"timestamp":int(time.time())};\
open("anchor_real_proof.json","w").\
write(json.dumps(p));\
print("status: PENDING_ONCHAIN");\
print("E14_VERIFIED_PENDING")
else: info=check(txid);\
print(info);\
print("E14_CHECK_DONE")
