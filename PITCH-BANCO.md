# PITCH-BANCO - XA-TRUST - 21/11/2026

## Pitch de 2 linhas

Elas vendem dashboard e PDF que pedem confianca no fornecedor.
Eu vendo codigo que trava dinheiro sem prova.

Eu nao aprovo sozinho. Sem quorum 2, dentro da janela e sem veto,
o codigo bloqueia - e qualquer auditor prova isso em 1 comando,
ate em clone limpo no celular.

## Diagnostico

RegTech entrega: SaaS centralizado, dashboard, PDF. Depende de confiar no servidor do emissor.
XA-TRUST entrega: codigo deterministico autocontido. JCS + SHA-256 + Ed25519.
Replay em clone limpo, sem SaaS proprietario, sem segredo interno.

## Por que Clone Limpo e assimetria real

1. Zero dependencia do emissor. Passou so com Python no Android.
2. Auditabilidade soberana. Banco nao precisa contratar a nuvem do emissor para auditar.
3. Impossivel maquiar demo. Nao e tela gravada, e log de execucao completo.

## Regra de Governanca Global

Sem PROMOTED, sem pagamento. Sem E6 PASS + E7 PROMOTED, cadeia trava.
1 veto bloqueia. 1 aprovador sozinho nao libera.
Golden Rule: Sem verificacao independente, sem promocao.

VERIFIED(CLAIM-E7, SCOPE-E7) - por claim, nao global.
