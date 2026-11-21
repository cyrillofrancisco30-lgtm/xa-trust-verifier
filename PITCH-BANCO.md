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


## Inovação tecnológica

A inovação do XA-TRUST não está no uso isolado de algoritmos criptográficos existentes, mas na arquitetura que combina evidência criptográfica, verificação independente, reprodução técnica e governança por barreiras de promoção.

O objetivo é permitir que instituições financeiras substituam a confiança exclusiva em relatórios declaratórios por critérios técnicos verificáveis, com rastreabilidade e controle sobre a aceitação de evidências.

O XA-TRUST propõe uma camada independente entre a execução automatizada, a comprovação técnica e a decisão de aceitar uma operação ou liberar recursos.

Princípio central: nenhuma promoção de claim sem verificação independente.

### Por que é inovação e não só uso de algoritmo

1. Tecnológica: combina JCS + SHA-256 + Ed25519 em um fluxo único de evidência -> verificação -> decisão.
2. Operacional: o verificador roda em clone limpo, fora da infraestrutura do emissor. O banco não precisa confiar no fornecedor.
3. Financeira: a liberação de recursos passa a depender de uma barreira técnica (E6/E7) e não só de uma aprovação humana.
4. Governança: quórum de 2 + veto individual cria um ponto de controle que não existe no modelo atual de PDF/relatório.

### O que o XA-TRUST cria de novo
Antes: fornecedor declara -> banco confia -> banco paga.
Depois: fornecedor declara -> evidência é verificada de forma independente -> quórum aprova -> E6/E7 promove -> banco paga.

Sem verificação independente, não há promoção. Sem promoção, não há pagamento.

### Aplicação
Bancos, FINEP, BNDES, SEBRAE, fintechs e qualquer operação que precise provar antes de pagar.


Autor: Cyrillo - xa-trust-verifier