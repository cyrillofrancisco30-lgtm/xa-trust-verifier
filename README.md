# XA Trust Verifier v1.0.0

Projeto original de Cyrillo Francisco.

O XA Trust Verifier é uma ferramenta independente de verificação de evidências, projetada para avaliar integridade, consistência e condições de confiança.

> **Tese:** Não basta demonstrar que uma execução aconteceu.
> É necessário demonstrar quais afirmações aquela evidência autoriza, em qual escopo e sob quais condições de confiança.

---

## O que faz

- Verifica evidências de execução (E4)
- Verifica vínculo criptográfico (E5)
- Exige verificação independente para promover confiança (E6)
- Decide por claim, com escopo delimitado (E7)
- Verifica o pacote completo (verificação global)

## Regra congelada

    NO_INDEPENDENT_VERIFICATION -> NO_E7

Sem verificação independente, uma claim não é promovida a E7.

## Status atual

| Claim | Status |
| --- | --- |
| E4 — EXECUTION_EVIDENCE | PASS — execução e resultados observados no escopo dos testes |
| E5 — CRYPTOGRAPHIC_BINDING | SHA-256 observado; vinculação do manifesto interno pendente |
| E6 — INDEPENDENT_VERIFICATION | PENDING |
| E7 — SCOPED_TRUST_DECISION | NOT PROMOTED |

A execução observada aprovou 9/9 testes no workflow `verify`, associado ao commit `c9eb1f2f1fbeec704c1d4c7cb91f96aa3f41e0a0`.

O digest SHA-256 do arquivo ZIP não deve ser confundido com o hash interno de `evidence.json`.

E6 exige verificação independente, executada por implementação ou ambiente separado, com registro do procedimento, resultado e hashes dos artefatos examinados. Replay pode integrar esse procedimento, mas não é automaticamente sinônimo de verificação independente.

Registro fundamentado na execução e nos resultados anteriormente examinados.

## Verificação global

Duas decisões independentes:

**GLOBAL — Package Integrity Verification**
Avalia estrutura, canonicalização JCS, integridade e consistência do pacote.
Resultado: pacote íntegro ou pacote rejeitado.

**POR CLAIM — Claim-Scoped Trust Decision**
Avalia E4, E5 e E6 para determinar se uma afirmação específica pode alcançar E7.
Resultado: VERIFIED, INSUFFICIENT_EVIDENCE ou CONTRADICTED, conforme os critérios aplicáveis.

Regras:

- Se 1 claim falhar, o pacote global NÃO passa.
- Verificação global aprovada NÃO promove automaticamente nenhuma claim a E7.
- Cada claim continua com sua própria decisão, seu próprio escopo e sua própria condição de confiança.

A aprovação global atesta somente os critérios de integridade e consistência definidos para o pacote. Não constitui prova universal da veracidade semântica das claims nele contidas.

Regra fundamental: pacote íntegro não significa que todas as claims sejam verdadeiras ou estejam verificadas.

## Como usar

    python verify.py

Verifica `evidence.json` com JCS (RFC 8785) e gera o resultado da verificação.

## Benchmarking

Análise comparativa em `BENCHMARK.md`.

Classificação: Comparative Technical Analysis — Not an Independent Product Evaluation.

- **Chainloop:** Referência para guardar e organizar evidência em escala.
- **TestifySec / Witness:** Referência para coletar evidência durante o build.
- **Kusari:** Referência para rastreabilidade de dependências e SBOM.

XA-TRUST: adota como requisito normativo explícito a não promoção de uma claim a E7 sem verificação independente E6.

## Aviso legal

Projeto open-source de verificação de software.
Sem relação com X-Trust Inc., A-Trust GmbH, TRUST-X ou qualquer instituição financeira.