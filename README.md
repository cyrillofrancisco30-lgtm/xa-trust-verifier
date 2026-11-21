cat > README.md << 'EOF'
Evidência verificável de execução. Não é promessa, é prova.

Projeto original de Cyrillo Francisco.

Verificação de Sinistros - individual
Verificar 1 declaração: claim.json

Status - claim.json
VERIFICAÇÕES CRIPTOGRÁFICAS: APROVADO
E3: RELATADO
E4: ARTEFATO RELATADO
E5: VALIDAÇÃO CRIPTOGRÁFICA RELATADA
E6: VERIFICAÇÃO INDEPENDENTE PENDENTE
E7: NÃO ESTABELECIDO

Nenhuma homologação reivindicada. Nenhuma E7 reivindicada antes da E6.

Como verificar (E6) - claim.json
python3 verificar_claim.py

Esperado:

JCS canônico bate? Verdade
SHA-256 bate? Verdadeiro
Ed25519 assinatura VALIDA? Verdadeiro RESULTADO: VERIFICADO
canonical_sha256: cb65c565881f96c17b1cd6513439372972d8a75c30f45760771bcf0fa7457dba

---

E3 - Claim relatada
E3 é a declaração em si, com JCS canônico + SHA-256 + assinatura Ed25519.
Sem E3 não há nada para verificar.

Como verificar:
python3 verificar_claim.py

E7 - Decisão de confiança com escopo
E7 = E5 + E6 + PROMOÇÃO / GOVERNANÇA
Decisão por claim, não por lote ou projeto.
Regra congelada: NO_INDEPENDENT_VERIFICATION -> NO_E7

Como verificar (SUITE E7):
python3 e7_all_in_one.py

Esperado:
POS-E7-001 PROMOTED quorum 2 OK
NEG-E7-001 OK quorum insuficiente
NEG-E7-002 OK veto bloqueia
NEG-E7-003 OK fora da janela inicio
NEG-E7-004 OK fora da janela fim
NEG-E7-005 OK assinatura aprovacao invalida
NEG-E7-006 OK aprovador duplicado
NEG-E7-007 OK aprovador revogado
NEG-E7-008 OK E5 falha bloqueia promocao
SUITE v1.1.6.5 COMPLETA

Prova em clone limpo:
git clone https://github.com/cyrillofrancisco30-lgtm/xa-trust-verifier e7-check && cd e7-check && python3 e7_all_in_one.py
Resultado: SUITE v1.1.6.5 COMPLETA

Como verificar (SUITE E6):
python3 e6_all_in_one.py
Resultado: SUITE v1.1.6.4 COMPLETA
EOF
cat README.md