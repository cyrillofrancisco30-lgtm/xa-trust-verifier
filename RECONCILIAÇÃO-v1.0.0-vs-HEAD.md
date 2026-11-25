# Reconciliação — v1.0.0 vs HEAD

Data: 25/11/2026
Repo: xa-trust-verifier

Este arquivo não altera, não apaga e não rebaixa nenhuma homologação.
Ele só separa os escopos para não misturar resultados de versões distintas.

## 1. Freeze preservado

- Tag: v1.0.0
- Commit congelado: 06f7443
- HEAD atual da main: 168e197
- Conclusão: o freeze NÃO foi substituído. O HEAD é evolução posterior, não reescrita do freeze.

O que vale para a homologação E3-E7 é o que estava no freeze.

## 2. Status preservado

STATUS: HOMOLOGAÇÃO TÉCNICA INTEGRAL XA-TRUST — E3 a E7
VERIFIED(CLAIM-E7, SCOPE-E7)

- PROOF-2026-11-21.md preservado
- Verificação em clone limpo em 21/11/2026 preservada
- E6 v1.1.6.4 COMPLETA preservada
- E7 v1.1.6.5 COMPLETA preservada

Verificação é por claim, não global.
Governança é global transversal dentro do escopo declarado.

Golden Rule respeitada: Sem verificação independente, sem promoção.

## 3. Três escopos separados

### 3.1 Freeze v1.0.0 / EVIDENCE.md
- Vale: homologação E3-E7, testes E6/E7 registrados
- Limitação declarada naquele ciclo: assinatura era simulada / demonstrativa, ainda não Ed25519 real
- Não pode ser lido como: já era Ed25519 real naquele ciclo

### 3.2 Testes E6/E7
- Arquivos: e6_all_in_one.py, e7_all_in_one.py
- Vale: usam Ed25519 + RFC 8785 nos testes, com chaves efêmeras geradas no próprio código
- Não prova: que o verificar_claim.py do freeze usava o mesmo caminho

### 3.3 Implementação atual / README
- Vale: verificar_claim.py é apresentado como implementação de referência RFC 8785 (JCS) + Ed25519
- Não pode: retroagir e reescrever o que o EVIDENCE.md do freeze declarou

## 4. Ponto técnico em aberto — verify_independent.py

Observação registrada, sem rebaixamento de E3-E7:

- verify_independent.py usa json.dumps(sort_keys=True, separators=...) para canonicalizar
- Não chama a biblioteca rfc8785

Isso é tecnicamente relevante porque um verificador independente não deve compartilhar a mesma aproximação de canonicalização do emissor.

Status deste ponto: EM ABERTO / A RECONCILIAR
- Opção A: passar verify_independent.py para usar a biblioteca rfc8785
- Opção B: documentar explicitamente que, neste escopo, canonicalização = json.dumps com esses parâmetros, com divergência de JCS conhecida e aceita

Até uma das duas opções ser aplicada, verify_independent.py não deve ser apresentado como verificador JCS puro.

## 5. Conclusão

- E3-E7 continuam homologados no escopo do freeze
- HEAD atual é evolução, não invalidação do freeze
- Reconciliação feita: escopos separados, versões separadas, limitações preservadas
- Próximo passo técnico: resolver o item 4, sem tocar em E3-E7

Não pedimos confiança. Pedimos verificação.

