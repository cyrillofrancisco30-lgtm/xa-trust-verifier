import json, subprocess, sys, os
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
ORIG="claim_v2.json"
P=F=0
def run(p):
    r=subprocess.run([sys.executable,"xa_trust.py","--claim",p],capture_output=True,text=True)
    return r.stdout+r.stderr
def check(n,exp,p):
    global P,F
    out=run(p); ok=exp in out
    print(("PASS " if ok else "FAIL ")+n+" -> "+out.strip().splitlines()[-1][:80])
    P+=ok; F+=not ok
    if p!=ORIG and os.path.exists(p): os.remove(p)
def save(d,n):
    p=f"_t_{n}.json"; json.dump(d,open(p,"w")); return p
def load(): return json.load(open(ORIG))
check("T01 valida","VERIFIED",ORIG)
d=load(); d["claim"]["mensagem"]="ADULTERADO"
check("T02 payload","FAIL",save(d,"02"))
d=load(); d["canonical_sha256"]="0"*64
check("T03 sha256","FAIL",save(d,"03"))
d=load(); d["signature_b64"]="A"+d["signature_b64"][1:]
check("T04 assinatura","FAIL",save(d,"04"))
d=load()
np=Ed25519PrivateKey.generate().public_key().public_bytes(serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo).decode()
d["public_key_pem"]=np
check("T05 chave errada","FAIL",save(d,"05"))
d=load(); d["signature_b64"]="!!!NAO-E-BASE64!!!"
check("T07 base64","FAIL",save(d,"07"))
d=load()
rp=rsa.generate_private_key(65537,2048).public_key().public_bytes(serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo).decode()
d["public_key_pem"]=rp
check("T08 chave RSA","FAIL",save(d,"08"))
print(f"=== {P} PASS, {F} FAIL ===")
# --- T06 / T09 / T10 com claim re-assinada ---
import hashlib, base64
try:
 import rfc8785
except: rfc8785=None
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
def sign_claim(claim_dict):
    sk=Ed25519PrivateKey.generate()
    can=rfc8785.dumps(claim_dict).decode()
    sha=hashlib.sha256(can.encode()).hexdigest()
    sig=base64.b64encode(sk.sign(can.encode())).decode()
    pub=sk.public_key().public_bytes(serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo).decode()
    return {"claim":claim_dict,"canonical":can,"canonical_sha256":sha,"signature_b64":sig,"public_key_pem":pub}
# T06 replay: mesma claim 2x deve dar mesmo resultado (documenta sem anti-replay)
o1=run(ORIG); o2=run(ORIG)
print(("PASS " if "VERIFIED" in o1 and "VERIFIED" in o2 else "FAIL ")+"T06 replay 2x VERIFIED (sem nonce = replay aceito, limitacao documentada)")
# T09 E6: claim sem autor, mas assinada corretamente -> deve FAIL em E6
c={"projeto":"xa-trust-verifier","politica":"Politica de Evidencias","mensagem":"teste E6"}
p=save(sign_claim(c),"09")
print(("PASS " if "E6" in run(p) else "FAIL ")+"T09 E6 sem autor -> FAIL E6")
# T10 E7: claim sem politica -> deve FAIL em E6/E7
c2={"autor":"Cyrillo","projeto":"xa-trust-verifier","mensagem":"teste E7"}
p2=save(sign_claim(c2),"10")
print(("PASS " if "FAIL" in run(p2) else "FAIL ")+"T10 E7 sem politica -> FAIL")
