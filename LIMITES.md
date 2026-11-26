# Limites da Homologação — XA Trust

## O que este pacote É

- Demonstração verificável de que o sistema XA Trust executa as verificações declaradas
- Limitada aos claims, requisitos e evidências efetivamente verificados
- Verificável independentemente por qualquer parte via RFC 8785 + Ed25519

## O que este pacote NÃO É

- NÃO é autorização, certificação ou aprovação institucional emitida por Banco Central, CVM ou outro órgão regulador
- NÃO é validade universal de todos os claims
- NÃO é garantia de que claims futuros serão válidos
- NÃO é parecer jurídico

## Regras que não mudam

- Sem evidência de execução, sem promoção
- Sistema externo só gera observação / evidência. Nunca gera verificação XA-TRUST
- Um claim fora do escopo é rejeitado, mesmo com assinatura correta
- Global aqui significa governança transversal dos claims dentro do escopo declarado, não validade universal

## Como contestar

Qualquer pessoa pode re-verificar qualquer claim usando:
1. O claim canonizado por RFC 8785
2. O hash SHA256 do canonical
3. A assinatura Ed25519
4. A chave pública declarada no escopo

Não pedimos confiança. Pedimos verificação.