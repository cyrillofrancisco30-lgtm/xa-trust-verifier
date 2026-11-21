# XA-TRUST Verifier v2

Evidência verificável de execução. Não é promessa, é prova.

Projeto original de Cyrillo Francisco.

## Verificação de Claims - individual

Verifica 1 claim: claim.json

## Status
CRYPTOGRAPHIC CHECKS: PASS
E3: REPORTED
E4: ARTIFACT REPORTED
E5: CRYPTOGRAPHIC VALIDATION REPORTED
E6: PENDING_INDEPENDENT_VERIFICATION
E7: NOT ESTABLISHED

No homologation claimed. No E7 claimed before E6.

## Como verificar (E6)
python3 verificar_claim.py

Esperado:
1. JCS canonical bate? True
2. SHA-256 bate? True
3. Ed25519 assinatura VALIDA? True
RESULTADO: VERIFIED

canonical_sha256: cb65c565881f96c17b1cd6513439372972d8a75c30f45760771bcf0fa7457dba
