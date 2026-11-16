# BENCHMARK.md — v1.0

**Classificação:** Comparative Technical Analysis — Not an Independent Product Evaluation
**Projeto:** xa-trust-verifier
**Data:** 2026-11-15

> **Tese:** Não basta demonstrar que uma execução aconteceu.
> É necessário demonstrar quais afirmações aquela evidência autoriza, em qual escopo e sob quais condições de confiança.

**Escopo do XA-TRUST:** Verificação determinística de evidências, proveniência, integridade e decisões de confiança com escopo por claim.

---

## 1. Tabela comparativa

| Capacidade | XA-TRUST | Chainloop | TestifySec / Witness | Kusari |
| --- | --- | --- | --- | --- |
| Foco principal | Decisão de confiança por claim | Evidence store + SLSA L3 | Coleta de evidência em runtime | Grafo de dependência + SBOM |
| Evidência de execução | Sim, E4 | Sim | Sim, via `witness run` | Parcial, via SBOM |
| Vinculação ao commit | Sim, obrigatória | Sim | Sim | Sim |
| Proveniência | Sim, determinística | Sim, SLSA Provenance | Sim, in-toto | Sim, GUAC |
| SBOM | Não é foco | Sim, CycloneDX | Não é foco | Core |
| Assinatura | Não exigida nesta versão | Sim, Sigstore | Sim, Sigstore / SPIFFE / DSSE | Sim |
| Política | Sim, E4-E7 | Sim, Workflow Contract | Sim, OPA Rego | Sim, bloqueio de PR |
| Verificação independente E6 | Requisito normativo explícito | Não identificado como requisito normativo equivalente | Não identificado como requisito normativo equivalente | Não demonstrado na documentação consultada |
| Replay de execução | Capacidade dependente da implementação do protocolo de verificação | Não é foco | Capacidade dependente da implementação | Não demonstrado na documentação consultada |
| Claims com escopo delimitado E7 | Modelo explícito | Não identificado como requisito normativo equivalente | Não identificado como requisito normativo equivalente | Não identificado como requisito normativo equivalente |
| Regra de negação | `NO_INDEPENDENT_VERIFICATION -> NO_E7` | Não identificado como requisito normativo equivalente | Não identificado como requisito normativo equivalente | Não identificado como requisito normativo equivalente |
| Padrão | JCS RFC 8785 + E4-E7 próprio | SLSA, in-toto, Sigstore, OCI | in-toto, DSSE, ITE-5/6/7 | GUAC, SLSA, CycloneDX / SPDX |
| Tamanho | 1 verificador, determinístico | Plataforma completa | Framework / CLI | Plataforma enterprise |

## 2. Posicionamento

- **Chainloop:** Referência para guardar e organizar evidência em escala. Benchmark de arquitetura.
- **TestifySec / Witness:** Referência para coletar evidência *durante* o build, com tracing e política OPA. Benchmark de coleta.
- **Kusari:** Referência para responder "onde estou exposto?" quando surge uma CVE. Benchmark de rastreabilidade.
- **XA-TRUST:** Adota como requisito normativo explícito a não promoção de uma claim a E7 sem verificação independente E6.

## 3. Status observado — XA-TRUST

| Claim | Status |
| --- | --- |
| E4 — EXECUTION_EVIDENCE | PASS — execução e resultados observados no escopo dos testes |
| E5 — CRYPTOGRAPHIC_BINDING | SHA-256 observado; vinculação do manifesto interno pendente |
| E6 — INDEPENDENT_VERIFICATION | PENDING |
| E7 — SCOPED_TRUST_DECISION | NOT PROMOTED |

A execução observada aprovou 9/9 testes no workflow `verify`, associado ao commit `c9eb1f2f1fbeec704c1d4c7cb91f96aa3f41e0a0`.

O digest SHA-256 do arquivo ZIP não deve ser confundido com o hash interno de `evidence.json`.

## 4. E6 — Precisão

**Regra congelada:** `NO_INDEPENDENT_VERIFICATION -> NO_E7`

E6 exige verificação independente, executada por implementação ou ambiente separado, com registro do procedimento, resultado e hashes dos artefatos examinados. Replay pode integrar esse procedimento, mas não é automaticamente sinônimo de verificação independente.

## 5. Verificação global — Duas decisões independentes

**GLOBAL — Package Integrity Verification**
Avalia estrutura, canonicalização JCS, integridade e consistência do pacote.
Resultado: pacote íntegro ou pacote rejeitado.

**POR CLAIM — Claim-Scoped Trust Decision**
Avalia E4, E5 e E6 para determinar se uma afirmação específica pode alcançar E7.
Resultado: VERIFIED, INSUFFICIENT_EVIDENCE ou CONTRADICTED, conforme os critérios aplicáveis.

A aprovação global atesta somente os critérios de integridade e consistência definidos para o pacote. Não constitui prova universal da veracidade semântica das claims nele contidas.

Regra fundamental: pacote íntegro não significa que todas as claims sejam verdadeiras ou estejam verificadas.

## 6. Limites desta análise

Esta é uma análise técnica comparativa, não uma avaliação independente de produto.
Afirmações sobre concorrentes refletem a documentação consultada até 2026-11-15 e não constituem prova de ausência de capacidade.

## 7. Referências

- Chainloop: https://chainloop.dev/
- TestifySec / Witness: https://testifysec.com/
- Kusari: https://kusari.cloud/
- SLSA: https://slsa.dev/
- in-toto: https://in-toto.io/
- GUAC: https://guac.sh/

## 8. Roadmap para prova

1. **E5:** Publicar SHA-256 do `evidence.json` no manifesto interno.
2. **E6:** Documentar uma verificação independente, com procedimento, resultado e hashes, por implementação ou ambiente separado. Incluir replay quando aplicável.

---

### Aviso legal

Projeto open-source de verificação de software.
Sem relação com X-Trust Inc., A-Trust GmbH, TRUST-X ou qualquer instituição financeira.