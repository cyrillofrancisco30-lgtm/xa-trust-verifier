# XA-TRUST Verifier v2

Evidência verificável de execução. Não é promessa, é prova.

Projeto original de Cyrillo Francisco - Francisco Fernando Lopes Cyrillo.

## Verificação de Claims - individual

Verifica 1 claim: `xa-trust/evidence/claim.json`

Confere:
- JCS (RFC 8785) - canonicalização correta?
- SHA-256 - `digest_sha256` bate com `manifest_jcs`?
- Ed25519 - `signature_ed25519` é válida?
- API-12 - SHA256_PAYLOAD_MATCH

Se 1 falhar, esse claim é `FAIL`.

## Verificação Global - Scope

Verifica o lote inteiro de uma vez. Não verifica só 1 arquivo.

Scope da verificação global:
- Todos os `claim.json` em `xa-trust/evidence/`
- Todos os `manifest` de cada claim
- Todos os `digest_sha256`
- Todas as `signature_ed25519`
- API-22 - MERKLE_PROOF_VALID - a árvore Merkle fecha?
- Nenhum claim alterado depois de assinado
- Nenhum claim duplicado
- Nenhum claim faltando
- Ordem e integridade do lote inteiro

Resultado só é `VERIFIED GLOBAL` se TODOS passarem.
Se 1 falhar, o lote inteiro é `FAIL`.

## Como funciona

1. **Producer** cria o `manifest`
2. **JCS (RFC 8785)** -> `manifest_jcs`
3. **SHA-256** -> `digest_sha256`
4. **Ed25519** assina -> `signature_ed25519`
5. Arquivo gerado: `xa-trust/evidence/claim.json`

## Como verificar

Verificar 1 claim:
```bash
python3 xa-trust/verifier.py --claim xa-trust/evidence/claim.json

