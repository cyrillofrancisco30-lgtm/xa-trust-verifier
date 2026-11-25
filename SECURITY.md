# SECURITY - XA-TRUST Verifier v2

## Modelo de ameaça
Atacante pode ler, copiar, reenviar e modificar qualquer claim.
Não pode forjar assinatura Ed25519 sem a chave privada.

## Garantias verificadas

| Teste | Ataque | Resultado esperado | Resultado obtido |
| --- | --- | --- | --- |
| T01 | Claim válida | VERIFIED E3-E7 OK | ✅ PASS |
| T02 | Payload adulterado | FAIL: JCS nao bate | ✅ PASS |
| T03 | SHA-256 adulterado | FAIL: API-12 SHA falhou | ✅ PASS |
| T04 | Assinatura adulterada | FAIL: Assinatura INVALIDA | ✅ PASS |
| T05 | Chave pública trocada | FAIL: Assinatura INVALIDA | ✅ PASS |
| T06 | Replay da mesma claim | VERIFIED 2x (ver limitação) | ✅ PASS documentado |
| T07 | Assinatura base64 inválida | FAIL: Ed25519 erro | ✅ PASS |
| T08 | Chave RSA no lugar de Ed25519 | FAIL: Chave nao e Ed25519 | ✅ PASS |
| T09 | Claim sem `autor` | FAIL: E6 Auditoria falhou | ✅ PASS |
| T10 | Claim sem `politica` | FAIL: E6 Auditoria falhou | ✅ PASS |

**Resultado: 10/10 PASS**

## Como reproduzir


