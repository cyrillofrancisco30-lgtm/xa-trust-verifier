cat > ~/README.md << 'EOF'
# XA Trust — Verificador de Confiança

Um recibo só é VÁLIDO se passar em TUDO junto: assinatura + vigência + não revogado na emissão + claim de governança.

Construído do zero no Termux, E1 até E14, tudo com teste FAIL -> PASS.

## Regra de ouro
Recibo antigo, emitido antes da revogação/rotação, continua válido (história preservada).
Recibo novo, emitido com chave antiga ou revogada, rejeita.

## Verificação Global por Claims — Governança Global de Escopo
Não verificamos só um arquivo. Verificamos o escopo inteiro.

Cada claim carrega sua própria governança: quem pode emitir, para que escopo, em qual vigência, e sob qual política.

A verificação é global porque:
- Um claim só é válido se o escopo dele for válido
- Um claim fora do escopo é rejeitado, mesmo com assinatura correta
- A governança não é local do arquivo, é global do sistema
- Revogação, rotação e política valem para todos os claims daquele escopo ao mesmo tempo

Global aqui significa governança transversal dos claims dentro do escopo declarado, não validade universal de todos os claims.

Sem escopo, não há confiança. Sem governança, não há verificação global.

## Como verificar
git clone https://github.com/cyrillofrancisco30-lgtm/xa-trust-verifier.git
cd xa-trust-verifier
pip install -r requirements.txt
python3 e10_all_in_one.py

## RFC 8785 (JCS) — A base da prova

JSON normal não é determinístico. O mesmo dado pode ser escrito de formas diferentes e continuar sendo o mesmo JSON. Se cada programa escrever de um jeito, o hash muda e a assinatura quebra, mesmo sem adulteração.

A RFC 8785 é o JSON Canonicalization Scheme (JCS). Ela define UMA única forma certa de escrever qualquer JSON:
- Chaves ordenadas por ordem Unicode
- Sem espaços desnecessários
- Sem quebras de linha
- Números, strings e escapes sempre do mesmo jeito

Mesmo conteúdo = mesmo texto = mesmo hash = mesma assinatura. Em qualquer linguagem, em qualquer máquina.

Sem JCS, sem prova. Sem canonical, não dá para confiar no hash.

## RFC 8785 na prática — Validado no Termux

Input: {"b":1,"a":2}
Canonical: {"a":2,"b":1}
SHA256: d3626ac30a87e6f7a6428233b3c68299976865fa5508e4267c5415c76af7a772

## Implementação de referência
verificar_claim.py é a implementação oficial. Utiliza RFC 8785 (JCS) + Ed25519.

Fluxo oficial:
1. Pega o claim
2. Canonicaliza com RFC 8785
3. Calcula SHA256 do canonical
4. Verifica a assinatura Ed25519 sobre o canonical, não sobre o JSON bagunçado

## Verificação Independente - VERIFIED

Verificador independente, sem confiar no emissor. Usa rfc8785 puro + Ed25519.

pip install rfc8785 cryptography
python3 verify_independent.py claim.json

Resultado real no Termux:
VERIFIED
proof_type: Ed25519+JCS-RFC8785
hash_claim_canonico: bd93dfeba74315e48ae5d0574fe1a4fa5e9a09f7d6e1b3e3a13d2c6cd1c40b
motivo: canonical RFC8785 + hash + assinatura Ed25519 OK

O que esse VERIFIED prova:
- Canonical guardado = canonical recalculado pela RFC 8785 pura
- Hash bate
- Assinatura Ed25519 válida para a chave v2

## Demo
e10_all_in_one.py é apenas demonstração de fluxo. Utiliza HMAC + json dumps. Serve para entender o fluxo E3-E7, mas NÃO é a prova criptográfica final.

## Provas Criptográficas — E3 a E10
Cada etapa é uma prova, não uma promessa. FAIL -> PASS.

- E3 Vigência: recibo fora da vigência é rejeitado, mesmo com assinatura válida.
- E4 Revogação: se já estava revogado na emissão, rejeita. Se foi revogado depois, o recibo antigo continua válido.
- E5 Governança: claim sem claim de governança xa-trust-v1 é rejeitado.
- E6 Política: claim fora da política do escopo é rejeitado.
- E7 Auditoria: toda decisão deixa rastro verificável, com timestamp de emissão, timestamp de verificação, kid da chave, hash do claim canônico, decisão e motivo.
- E8 Revogação no tempo: vale o status no momento da emissão, não no momento da verificação.
- E9 Rotação: chave nova não invalida recibo antigo válido.
- E10 Ponta a ponta: emitir -> verificar -> revogar -> rodar -> antigo ainda vale.

Prova final em verificar_claim.py: RFC 8785 (JCS) + Ed25519. Sem JCS, sem prova. Sem Ed25519, sem confiança.

## E11 até E14 — Prova Pública
O mercado de praxe para em E7 (prova interna). O XA Trust vai além:

- E11-E12: Cadeia de provas — cada prova amarra a anterior.
- E13-E14: Âncora no Bitcoin via OP_RETURN — qualquer pessoa pode verificar sem precisar da empresa.

Arquivos:
- e14_real_anchor.py - ancora a prova real no Bitcoin
- anchor_real_proof.json - prova ancorada
- fix14.py - verificação do E14

E7 = verificação interna, padrão de mercado
E14 = prova pública, nível cartório digital

Não pedimos confiança. Pedimos verificação.
EOF
## ✅ XA Finance - Verificado na Nuvem (2026-11-25)
Status: VERIFIED - Run #109 - 9 passed + REPLAY_OK
E14 Ancora Real | E15 Publica Ancora | E16 Verifica Independente | E17 End-to-End

## Homologação regulatória

Homologação regulatória demonstrada no escopo dos claims verificados, mediante políticas e requisitos regulatórios explicitamente declarados, evidências vinculadas e aprovação pelos gates de verificação independente e promoção do XA-TRUST. Esta demonstração é limitada aos claims, requisitos e evidências efetivamente verificados. Não constitui autorização, certificação ou aprovação institucional emitida por Banco Central, CVM ou outro órgão regulador.

Com identificador independente RFC8785: o identificador é o hash do claim canonizado por JCS / RFC8785, verificável independentemente por qualquer parte, sem depender do servidor de origem.

Distinção preservada:
- Homologação demonstrada pelo sistema: resultado verificável, restrito ao escopo dos claims aprovados.
- Autorização institucional: reconhecimento formal emitido pela autoridade competente.
