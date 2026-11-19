# XA-TRUST Verifier v2

Evidência verificável de execução. Não é promessa, é prova.

Projeto original de Cyrillo Francisco - Francisco Fernando Lopes Cyrillo.

## Como funciona

1. **Producer** cria o `manifest` com o que foi executado
2. **JCS (RFC 8785)** canonicaliza o manifest -> `manifest_jcs`
3. **SHA-256** do `manifest_jcs` -> `digest_sha256`
4. **Ed25519** assina o `manifest_jcs` -> `signature_ed25519`

Arquivo gerado: `xa-trust/evidence/claim.json`

## O que ele verifica

- **API-12 - SHA256_PAYLOAD_MATCH:** o hash bate com o payload?
- **API-22 - MERKLE_PROOF_VALID:** a prova de inclusão é válida?
- **JCS + SHA-256 + Ed25519:** canonicalização, digest e assinatura conferem?

Se um falhar, o resultado é `FAIL`.

## Arquivos

- `xa-trust/producer.py` - gera `evidence/claim.json`
- `xa-trust/verifier.py` - verificação independente
- `verify_aep.py` - verificação de evidência
- `evidence.json` - evidência de exemplo
- `.github/workflows/` - roda a verificação a cada push

## Como verificar em 30 segundos

```bash
pip install rfc8785 cryptography
python3 xa-trust/producer.py
python3 xa-trust/verifier.py


VERIFIED - JCS + SHA256 + Ed25519 OK

