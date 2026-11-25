# XA Trust — Verificador de Confiança

Um recibo só é VÁLIDO se passar em TUDO junto: assinatura + vigência + não revogado na emissão + claim de governança.

Construído do zero no Termux, E1 até E10, tudo com teste FAIL -> PASS.

## Regra de ouro

- Recibo antigo, emitido antes da revogação/rotação, continua válido (história preservada).
- Recibo novo, emitido com chave antiga ou revogada, rejeita.

## Verificação Global por Claims — Governança Global de Escopo

Não verificamos só um arquivo. Verificamos o escopo inteiro.

Cada claim carrega sua própria governança: quem pode emitir, para que escopo, em qual vigência, e sob qual política.

A verificação é global porque:
- Um claim só é válido se o escopo dele for válido
- Um claim fora do escopo é rejeitado, mesmo com assinatura correta
- A governança não é local do arquivo, é global do sistema
- Revogação, rotação e política valem para todos os claims daquele escopo ao mesmo tempo

Sem escopo, não há confiança. Sem governança, não há verificação global.

## Como verificar

git clone https://github.com/cyrillofrancisco30-lgtm/xa-trust-verifier.git
cd xa-trust-verifier
pip install -r requirements.txt
python3 e10_all_in_one.py

## Implementação de referência

verificar_claim.py é a implementação oficial.
Utiliza RFC 8785 (JCS) + Ed25519.

Validado no Termux:
Input: {"b":1,"a":2}
Canonical: {"a":2,"b":1}
SHA256: d3626ac30a87e6f7a6428233b3c68299976865fa5508e4267c5415c76af7a772

## Demo

e10_all_in_one.py é apenas demonstração de fluxo.
Utiliza HMAC + json.dumps.
Serve para entender o fluxo E3-E7, mas NÃO é a prova criptográfica final.

Não pedimos confiança. Pedimos verificação.

