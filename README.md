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
```bash
git clone https://github.com/cyrillofrancisco30-lgtm/xa-trust-verifier.git
cd xa-trust-verifier
pip install -r requirements.txt
python3 e10_all_in_one.py


