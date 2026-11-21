# XA-TRUST - PITCH BANCO

XA-TRUST transforma confiança declaratória em evidência verificável,
permitindo que instituições financeiras condicionem decisões e liberações
de recursos à comprovação independente de requisitos técnicos e de governança.

## O problema
Hoje o banco paga com base em relatório do fornecedor.
O fornecedor controla a medição, o relatório e a prova.
Isso é confiança, não verificação.

## A solução
1. Evidência criptográfica: JCS + SHA-256 + Ed25519
2. Verificação independente: banco reproduz em clone limpo, no seu ambiente
3. Governança por quórum: 2 aprovadores independentes
4. Veto individual: 1 veto trava a promoção
5. Promoção controlada: E6 e E7 como barreiras
6. Controle financeiro: sem E6 PASS + E7 PROMOTED, sem pagamento

## Regra de governança
NO INDEPENDENT VERIFICATION → NO E7 PROMOTION
VERIFIED é por claim, não global.

## Prova
python3 verificar_claim.py -> VERIFIED
Arquivos: claim.json + verificar_claim.py + log de execução

## O que já está provado
Declaração assinada, não alterada e verificável de forma independente.

## O que está em homologação
Bloqueio financeiro por quórum, veto e promoção E6/E7
em Azure + Terraform, com acesso limitado e sem dados críticos.

Autor: Cyrillo - xa-trust-verifier