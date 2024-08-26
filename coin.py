import hashlib
import time
import rsa

class Transaction:
    def __init__(self, sender, receiver, amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.signature = None
    def calculate_hash(self):
        return f"{self.sender}{self.receiver}{self.amount}".encode('utf-8')
    def sign_transaction(self, private_key):
        self.signature = rsa.sign(self.calculate_hash(), private_key, 'SHA-256')
    def is_valid(self):
        if not self.signature:
            return False
        try:
            rsa.verify(self.calculate_hash(), self.signature, self.sender)
            return True
        except rsa.VerificationError:
            return False
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
    def valid_transactions(self):
        return all(trans.is_valid() for trans in self.transactions) 

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
        if transaction.is_valid():
            self.pending_transactions.append(transaction)
        else:
            print('Transaction nyet valido')
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

