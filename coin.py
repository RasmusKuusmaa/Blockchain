import hashlib
import time

class Transaction:
    def __init__(self, sender, receiver, amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
    def __str__(self):
        return f"{self.sender} -> {self.receiver}: {self.amount}"
class Block:
    def __init__(self, timestamp, transactions, previous_hash = ''):
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()
    
    
    def calculate_hash(self):
        block_string = f"{self.timestamp}{self.transactions}{self.previous_hash}{self.nonce}"
        return hashlib.sha256(block_string.encode('utf-8')).hexdigest()
    def mine_block(self, difficulty):
        prefix = '0' * difficulty
        while( not self.hash.startswith(prefix)):
            self.nonce += 1
            self.hash = self.calculate_hash()
            print(self.hash)
class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.difficulty = 2
        self.pending_transactions = []
        self.mining_reward = 20
    
    def create_genesis_block(self):
        return Block(time.time(), [], "0")
    
    def get_latest_block(self):
        return self.chain[-1]
    
    def mine_pending_transactions(self, miner_address):
        block = Block(time.time(), self.pending_transactions)
        block.mine_block(self.difficulty)
        print('block mined')
        self.chain.append(block)
        self.pending_transactions = [Transaction(None, miner_address, self.mining_reward)]
    def create_transaction(self, transaction):
        self.pending_transactions.append(transaction)
    def get_balance(self, address):
        balance = 0
        for block in self.chain:
            for tr in block.transactions:
                if tr.receiver == address:
                    balance += tr.amount
                if tr.sender == address:
                    balance -= tr.amount
        return balance
    def check_chain_validity(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            if current_block.hash != current_block.calculate_hash():
                return False
            if current_block.previous_hash != previous_block.hash:
                return False
        return True

amjkcoin = Blockchain()
amjkcoin.create_transaction(Transaction('test1', 'test2', 100))
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
   