# XA-TRUST — Infra de Governança Verificável por Claim

> Não é selo. Não é PDF. É prova executável.
>
> Sem verificação independente, sem promoção. Ponto.

## FROZEN — XA-TRUST GOLDEN RULE OF VERIFICATION

```
IDENTITY ≠ INTEGRITY ≠ SEMANTIC TRUTH

E7 — CLAIM-SCOPED VERIFIED
iff
E3_EXECUTION_IDENTITY
∧ E4_RESULT_EVIDENCE
∧ E5_BINDING_INTEGRITY
∧ E6_INDEPENDENT_VERIFICATION
∧ APPLICABLE_PROMOTION_POLICY
```

`+` não é soma. É conjunção cumulativa. Nenhuma evidência compensa outra.

### Axiomas de Não-Compensação

- E3 presente ∧ E4 faltando → NO_PROMOTION
- E4 presente ∧ E5 inválido → NO_PROMOTION
- E5 válido ∧ E6 faltando → NO_PROMOTION
- E6 válido ∧ POLICY não satisfeita → NO_PROMOTION

> VALIDITY OF THE EVIDENCE ≠ VALIDITY OF THE CLAIM

A primeira é propriedade da cadeia de evidência.
A segunda é conclusão claim-scoped, condicionada à verificação semântica aplicável.

### Escopo

```
VERIFIED(CLAIM-X, SCOPE-X) ↛ VERIFIED(CLAIM-Y, SCOPE-Y)
VERIFIED(CLAIM-X, SCOPE-X) ↛ GLOBAL_VERIFIED
```

E7 = VERIFIED significa apenas:

> Este claim específico satisfaz os requisitos de evidência, binding, integridade, verificação independente e política de promoção definidos para este escopo.

Não significa que o sistema inteiro é verdadeiro, seguro ou globalmente verificado.

---

## Cadeia de Evidência

```
81b79a5
  │
  ▼
08d69bc — SPECIFICATION / CONTRACT EVIDENCE
  │ 213 linhas no README
  │ RFC 8785 + SHA-256 + Ed25519 + TRUST_OK + Acceptance Rule
  │ DecisionRequest → Identity → Authorization → Deterministic Execution
  │ → DecisionEvent → DEP Assembly → Canonicalização → Binding Hash
  │ → Assinatura → Ledger → AuditProof → Independent Verifier → Replay → TRUST_OK
  │
  ▼
4dd79f2 — OPERATIONAL WORKFLOW IMPLEMENTATION
  │
  ▼
e80501a — CONCRETE REPOSITORY MUTATION
  │
  ▼
[CONCRETE RUN]
  │
  ▼
[OBSERVED RESULT]
  │
  ▼
[INDEPENDENT VERIFICATION]
```

O commit `08d69bc` é classificado como CONCRETE SPECIFICATION / CONTRACT EVIDENCE.

Ele não confunde especificação com prova operacional. Ele define que o próximo passo é o verificador executável.

---

## O Que Este Repositório Prova

### E3 — EXECUTION IDENTITY

`claim.json` + JCS + SHA-256 + Ed25519.

Se mudar 1 letra, a assinatura quebra.

### E6 — Suite Roda do Zero

```bash
python3 e6_all_in_one.py
# SUITE v1.1.6.4 COMPLETA
```

### E7 — Governança Funciona

```bash
python3 e7_all_in_one.py
# SUITE v1.1.6.5 COMPLETA — 9 testes
```

- Sem verificação independente = sem promoção
- Quorum 2 exigido
- Veto trava
- Fora da janela não passa
- Aprovador inválido não passa
- Promoção só se tudo passar

### GitHub Workflow — Correção Crítica

A cadeia abaixo é INVÁLIDA como regra de promoção:

```
workflow_run.completed → hash → Merkle → VERIFIED
```

Porque:

```
WORKFLOW_RUN_COMPLETED ↛ TEST_PASSED
WORKFLOW_CONCLUSION_SUCCESS ↛ CLAIM_CONFORMANCE
ARTIFACT_RETRIEVED ↛ ARTIFACT_TRUST
HASH_VALID ↛ SEMANTIC_CORRECTNESS
MERKLE_VALID ↛ CLAIM_TRUTH
E5_CRYPTOGRAPHIC_BINDING ↛ E7_VERIFIED
```

A cadeia correta é:

```
workflow_run.completed
  ↓
event.workflow_run.id
  ↓
GET /actions/runs/{same_id}
  ↓
eventRun.id === apiRun.id
  ↓
E3 — EXECUTION_EVENT_EVIDENCE
  ↓
E4 — TEST / RESULT EVIDENCE
  ↓
E5 — CRYPTOGRAPHIC_BINDING
  ↓
E6 — INDEPENDENT_VERIFICATION
  ↓
PROMOTION POLICY
  ↓
E7 — CLAIM-SCOPED VERIFIED
```

Validação obrigatória contra substitution:

```js
if (Number(eventRun.id) !== run.id) {
  throw new Error("WORKFLOW_RUN_ID_MISMATCH");
}
```

---

## O Que Este Repositório NÃO Prova

- Que o projeto inteiro está aprovado
- Que a claim é verdadeira no mundo real — só que a cripto dela está certa
- Que tem auditoria externa formal
- Que tem homologação oficial

---

## Posicionamento

Infra de confiança programável.
Primeira no Brasil a provar governança por claim, com quorum, veto e janela, em clone limpo.

Para bancos, governo, saúde e empresas reguladas:

> Governança que você prova em 1 comando, não em PDF.

