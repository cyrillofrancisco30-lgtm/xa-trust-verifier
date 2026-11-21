# XA-TRUST - PITCH BANCO

## Tese
Elas vendem dashboard e PDF que pedem confiança no fornecedor.
Eu vendo código que trava dinheiro sem prova.

## Diagnóstico
Hoje o banco paga com base em relatório do fornecedor.
O fornecedor controla a medição, o relatório e a prova.
Isso é confiança, não verificação.

## Diferencial XA-TRUST
1. JCS + SHA-256 + Ed25519: cada declaração é canônica, com hash e assinatura verificável.
2. Replay em clone limpo: o banco reproduz a verificação no seu próprio ambiente, sem depender da infraestrutura do fornecedor.
3. Sem SaaS proprietário: verificação com código aberto e dependências mínimas.
4. Governança por quórum: 2 aprovadores independentes.
5. Veto individual: 1 veto trava a promoção.
6. Bloqueio de pagamento: sem E6 PASS + E7 PROMOTED, sem pagamento.

## Regra de Governança Global
NO INDEPENDENT VERIFICATION → NO E7 PROMOTION

VERIFIED é por claim, não global.
Cada claim precisa ser verificado individualmente.

## Prova Reprodutível
O auditor pode reproduzir a verificação em 1 comando, em ambiente com Python 3.11+ e os arquivos deste repositório:

python3 verificar_claim.py

Resultado esperado: VERIFIED

Artefatos para reprodução:
- claim.json
- verificar_claim.py
- Log de execução em clone limpo

## O que o XA-TRUST prova hoje
Prova que uma declaração específica foi assinada, não alterada e pode ser verificada de forma independente.

## O que ainda está em homologação
Implementação completa do bloqueio financeiro por quórum, veto e promoção E6/E7 em ambiente Azure + Terraform.
Homologação a ser executada com acesso limitado, sem dados críticos do cliente.