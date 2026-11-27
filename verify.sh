#!/bin/bash
echo "=== XA-TRUST-VERIFIER ==="
echo "1. Checando SHA256..."
sha256sum -c xa-proof/SHA256.txt
echo ""
echo "2. Checando OTS..."
ots info xa-proof/teste.txt.ots | grep -i "977624"
echo ""
echo "3. Checando bloco no mempool..."
HASH=$(curl -s https://mempool.space/api/block-height/977624)
curl -s https://mempool.space/api/block/$HASH | grep -o '"merkle_root":"[^"]*"'
echo ""
echo "Se os 3 baterem = PROVA VÁLIDA ✅"
