a=open("e14_real_anchor.py").read().splitlines()
b=[]
for l in a:
 if l.startswith(' p={"xa":"E14"') or l.startswith('p={"xa"'):
  continue
 if "anchor_real_proof" in l and "write" in l:
  continue
 b.append(l)
s="\n".join(b)
s=s.replace('print("status: PENDING_ONCHAIN")','p={}\np["xa"]="E14"\np["merkle_root"]=root\np["op_return_hex"]=op\np["status"]="PENDING_ONCHAIN"\nopen("anchor_real_proof.json","w").write(json.dumps(p,indent=2))\nprint("status: PENDING_ONCHAIN")')
open("e14_real_anchor.py","w").write(s)
print("FIX_OK")
