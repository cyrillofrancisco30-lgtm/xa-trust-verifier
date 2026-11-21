# XA-TRUST Verifier v2

Evidencia verificavel de execucao. Nao e promessa, e prova.

Projeto original de Cyrillo Francisco - Francisco Fernando Lopes Cyrillo.

## Verificacao de Claims - individual
Verifica 1 claim: xa_trust.py

Confere:
- JCS (RFC 8785) - canonicalizacao correta?
- SHA-256 - digest_sha256 bate com manifest_jcs?
- Ed25519 - signature_ed25519 e valida?
- API-12 - SHA256_PAYLOAD_MATCH

Se 1 falhar, esse claim e FAIL.

## Verificacao Global - Scope
Verifica o lote inteiro de uma vez. Nao verifica so 1 arquivo.

Scope:
- Todos os claim.json em evidence/
- Todos os manifest de cada claim
- Todos os digest_sha256
- Todas as signature_ed25519
- API-22 - MERKLE_PROOF_VALID - a arvore Merkle fecha?
- Nenhum claim alterado depois de assinado
- Nenhum claim duplicado
- Nenhum claim faltando
- Ordem e integridade do lote inteiro

Resultado so e VERIFIED GLOBAL se TODOS passarem. Se 1 falhar, o lote inteiro e FAIL.

## Como funciona
1. JCS (RFC 8785) -> manifest_jcs
2. SHA-256 -> digest_sha256
3. Ed25519 assina -> signature_ed25519
4. Arquivo gerado: claim.json

## Como verificar
python3 xa_trust.py --claim claim.json
python3 -m pytest -q
