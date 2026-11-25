def check(k,signed_at):
  if signed_at < k['valid_from']: return False
  if signed_at > k['valid_until']: return False
  if 'revoked_at' in k and signed_at > k['revoked_at']: return False
  return True
old={'valid_from':100,'valid_until':200,'revoked_at':200}
new={'valid_from':201,'valid_until':9999}
t1=check(old,150)==True
t2=check(old,250)==False
t3=check(new,250)==True
t4=check(old,201)==False
print('E9 recibo antigo valido:',t1)
print('E9 chave antiga apos rotacao rejeita:',t2)
print('E9 chave nova assina novo:',t3)
print('E9 apos revogacao rejeita:',t4)
print('E9 PASS' if all([t1,t2,t3,t4]) else 'E9 FAIL')
