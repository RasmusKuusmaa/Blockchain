import coin
amjkcoin = coin.Blockchain()
amjkcoin.create_transaction(coin.Transaction('test1', 'test2', 100))
print('startmine')
amjkcoin.mine_pending_transactions('testminer')
amjkcoin.mine_pending_transactions('miner2')
print("test1", amjkcoin.get_balance('test1'))
print("test2", amjkcoin.get_balance('test2'))
print("testminer", amjkcoin.get_balance('testminer'))


for block in amjkcoin.chain:
    print("Transactions:")
    for i in block.transactions:
        print(i)
    print(f"Previous Hash: {block.previous_hash}")
    print(f"Hash: {block.hash}")
   