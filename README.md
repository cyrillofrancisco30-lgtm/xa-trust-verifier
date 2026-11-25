# XA Trust — Verificador de Confiança

Um recibo só é VÁLIDO se passar em TUDO junto: assinatura + vigência + não revogado na emissão + claim de governança.

Construído do zero no Termux, E1 até E10, tudo com teste FAIL -> PASS.

## Ciclo completo

| Etapa | O que prova |
| --- | --- |
| E1 | Identidade |
| E2 | Assinatura |
| E3 | Vigência |
| E4 | Revogação |
| E5 | Governança (`xa-trust-v1`) |
| E6 | Política |
| E7 | Auditoria |
| E8 | Revogação no tempo |
| E9 | Rotação sem quebrar o passado |
| E10 | Ponta a ponta: emitir -> verificar -> revogar -> rodar -> antigo ainda vale |

## Regra de ouro

- Recibo antigo, emitido antes da revogação/rotação, **continua válido** (história preservada).
- Recibo novo, emitido com chave antiga ou revogada, **rejeita**.

## Como rodar

```bash
python3 e10_all_in_one.py

