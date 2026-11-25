# Xa Finance AI - Loop Deterministico Bit-a-Bit

> A verdade aqui nao depende de confianca, nem de log, nem de infra.
> Depende so de matematica + dados.

## 1) Ordem global imutavel (Journal)

seq BIGINT NOT NULL
ORDER BY seq ASC

- Fonte unica da verdade
- Totalmente ordenado
- Sem ambiguidade entre multiplos workers

Validacao: assert current_seq > last_seq
Elimina race conditions na leitura.

## 2) Snapshot deterministico dos dados (items)

items_sorted = sorted(items, key=lambda x: (x[0], json.dumps(x[1], sort_keys=True)))

- Ordem FORCADA
- JSON canonico (sort_keys=True)
- Independente de runtime / maquina

Serializacao final: len(h).to_bytes(4, "big") + h
Remove ambiguidade de concatenacao.

## 3) Merkle Root com domain separation

H(b"\x00" + canonical_serialize(i))

- Prefixo 0x00 separa dominio de leaf
- Arvore binaria deterministica
- Mesmo conjunto -> mesma raiz SEMPRE

## 4) GBID deterministico (UUIDv5)

name = H(serialized + u64_be(seq))
gbid = uuid.uuid5(NAMESPACE_UUID, name.hex())

Depende apenas de: conteudo, ordem, seq.
Mesmo input -> mesmo ID global.

## 5) Batch Hash com separacao de dominio

batch_hash = H(b"\x02" + len(serialized).to_bytes(4, "big") + serialized + b"\x03" + entry.merkle_root + b"\x04" + u64_be(entry.seq))

Evita colisao entre estruturas e ataques de replay.

## 6) Assinatura deterministica

sign_input = H(b"\x05" + entry.merkle_root + entry.batch_hash + entry.gbid.bytes + u64_be(entry.seq) + entry.signer_id.encode())

- Ed25519 = deterministico por padrao
- Inclui: conteudo, estrutura, identidade, ordem global
- Replay SEMPRE valida igual

## 7) Anchor criptografico final

anchor_hash = H(b"\x06" + entry.merkle_root + entry.signature + entry.gbid.bytes)

Liga: dados + assinatura + identidade.
Fecha o ciclo criptografico.

## 8) Auditoria independente (BigQuery)

SELECT seq, payload FROM xa_finance.journal_entries ORDER BY seq

- Append-only
- Ordenacao garantida
- Loop: verify(entry, pubkey)
- Reexecucao completa sem confiar no sistema original

## Propriedades formais

- Determinismo forte: mesmo input -> mesmo gbid, hash, assinatura, anchor
- Reprodutibilidade total: qualquer auditor faz replay(journal) -> REPLAY_OK
- Imutabilidade verificavel: 1 byte alterado quebra em serialized / merkle / gbid / batch_hash / signature / anchor
- Anti-ataques: reordering (seq), replay (gbid+seq), colisao estrutural (len+tags), forgery (Ed25519), tampering (replay)

## Interpretacao

Um ledger deterministico verificavel externamente.
Sem precisar de Raft, Paxos ou blockchain interno.
O journal + seq ja e o consenso.

## Status

Deterministico: SIM
Reprodutivel: SIM
Auditavel externamente: SIM
Multi-node seguro: SIM
Bit-a-bit consistente: SIM

## Implementacao oficial

Repo: https://github.com/cyrillofrancisco30-lgtm/xa-trust-verifier
PROOF: https://github.com/cyrillofrancisco30-lgtm/xa-trust-verifier/blob/main/PROOF-2026-11-21.md
