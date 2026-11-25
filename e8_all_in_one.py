import time
TTL=300
def check(m,kid,now):
  if kid in m.get('revoked',[]): return False
  if now-m.get('issued_at',now)>TTL: return False
  return True
now=int(time.time())
t1=check({'revoked':['k1'],'issued_at':now},'k1',now)==False
t2=check({'revoked':[],'issued_at':now},'k1',now)==True
t3=check({'revoked':[],'issued_at':now-9999},'k1',now)==False
print('E8 revogado rejeita:',t1)
print('E8 valido aceita:',t2)
print('E8 cache velho rejeita:',t3)
print('E8 PASS' if all([t1,t2,t3]) else 'E8 FAIL')
