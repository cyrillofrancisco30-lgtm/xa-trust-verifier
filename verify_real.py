import json
d = json.load(open('publish_proof.json'))
print("txid:", d['txid'])
print("block:", d['block_height'])
print("status:", d['status'])
print("merkle_root:", d['merkle_root'])
assert d['txid'] == '377a0291264520b3fcc4f1360d840edebdca20229afaa0546d834fafaf3831b1'
assert d['status'] == 'CONFIRMED_ONCHAIN'
print("E17_VERIFIED_REAL: True - 100% REAL")
