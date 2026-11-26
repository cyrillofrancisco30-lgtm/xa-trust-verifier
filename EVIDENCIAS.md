# Evidências — Pacote de Homologação XA Trust

## Como verificar

Cada evidência é verificável independentemente, sem depender do servidor de origem.

## E3 - Vigência
Recibo fora da vigência é rejeitado, mesmo com assinatura válida.
Teste: FAIL -> PASS

## E4 - Revogação
Se já estava revogado na emissão, rejeita.
Se foi revogado depois, o recibo antigo continua válido.
Teste: FAIL -> PASS

## E5 - Governança
Claim sem claim de governança xa-trust-v1 é rejeitado.
Teste: FAIL -> PASS

## E6 - Política
Claim fora da política do escopo é rejeitado.
Teste: FAIL -> PASS

## E7 - Auditoria
Toda decisão deixa rastro: timestamp de emissão, timestamp de verificação, kid da chave, hash do claim canônico, decisão e motivo.
Teste: FAIL -> PASS

## E8 - Revogação no tempo
Vale o status no momento da emissão, não no momento da verificação.
Teste: FAIL -> PASS

## E9 - Rotação
Chave nova não invalida recibo antigo válido.
Teste: FAIL -> PASS

## E10 - Ponta a ponta
Emitir -> verificar -> revogar -> rodar -> antigo ainda vale.
Teste: FAIL -> PASS

## E11-E12 - Cadeia de provas
Cada prova amarra a anterior.
Teste: FAIL -> PASS

## E13-E14 - Âncora pública
Âncora no Bitcoin via OP_RETURN.
Qualquer pessoa pode verificar sem precisar da empresa.
Arquivos: e14_real_anchor.py, anchor_real_proof.json, fix14.py
Teste: FAIL -> PASS

## Prova criptográfica final

verificar_claim.py: RFC 8785 (JCS) + Ed25519
verify_independent.py: VERIFIED
hash_claim_canonico: bd93dfeba74315e48ae5d0574fe1a4fa5e9a09f7d6e1b3e3a13d2c6cd1c40b

Sem JCS, sem prova. Sem Ed25519, sem confiança.