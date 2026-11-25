# XA-TRUST v1.0.0 - Evidence Pack

Tag: v1.0.0
Commit: 06f7443
Baseline: artifacts/BASELINE.txt
Hashes: artifacts/SHA256SUMS.txt

## Reproducao em clone limpo
git clone https://github.com/cyrillofrancisco30-lgtm/xa-trust-verifier.git xa-trust-clean
cd xa-trust-clean
python3 e10_all_in_one.py
Resultado: E10 PASS

## Escopo
E1-E10 ciclo fechado. Verificacao = assinatura + vigencia + nao revogado na emissao + claim de governanca.

## Limitacoes conhecidas
- Assinatura simulada / demonstrativa, nao Ed25519 real ainda
- Sem rede, sem cache persistente, sem relogio confiavel externo
- Chaves privadas nao incluidas no repo

## Regra de ouro
Recibo antigo, emitido antes da revogacao/rotacao, continua valido.
Recibo novo, com chave antiga ou revogada, rejeita.
