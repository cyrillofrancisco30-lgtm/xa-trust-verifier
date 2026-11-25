import hashlib, hmac, json
def sign(k, m): return hmac.new(k.encode(), json.dumps(m, sort_keys=True).encode(), hashlib.sha256).hexdigest()
def verify(r, keys, revoked):
    # 1. assinatura
    s = r.copy(); sig = s.pop("sig")
    if sign(r["kid"], s) != sig: return False
    # 2. chave ativa na emissao
    if r["ts"] < keys[r["kid"]]["from"] or r["ts"] >= keys[r["kid"]].get("to", 999999): return False
    # 3. nao revogada na emissao
    if r["kid"] in revoked and r["ts"] >= revoked[r["kid"]]: return False
    # 4. claim de governanca
    if r.get("gov") != "xa-trust-v1": return False
    return True

keys = {"k1": {"from": 0, "to": 30}, "k2": {"from": 30, "to": 999999}}
revoked = {}

def issue(kid, ts, gov="xa-trust-v1"):
    r = {"kid": kid, "ts": ts, "gov": gov, "data": "e10"}
    r["sig"] = sign(kid, r)
    return r

# 1. emite + verifica
r1 = issue("k1", 10)
t1 = verify(r1, keys, revoked)
print("E10 emite e verifica:", t1)
# 2. revoga k1 em 20, roda para k2 em 30
revoked["k1"] = 20
# 3. recibo antigo ainda vale (historia preservada)
t2 = verify(r1, keys, revoked)
print("E10 antigo apos revogar+rodar:", t2)
# 4. novo com chave antiga rejeita
r_old = issue("k1", 40)
t3 = not verify(r_old, keys, revoked)
print("E10 novo com chave antiga rejeita:", t3)
# 5. novo com chave nova assina
r2 = issue("k2", 40)
t4 = verify(r2, keys, revoked)
print("E10 novo com chave nova:", t4)
# 6. recibo apos revogacao da k2 rejeita
revoked["k2"] = 50
r_late = issue("k2", 60)
t5 = not verify(r_late, keys, revoked)
print("E10 apos revogacao rejeita:", t5)
print("E10 PASS" if all([t1, t2, t3, t4, t5]) else "E10 FAIL")
