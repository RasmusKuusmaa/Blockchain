'''
import hashlib
import json
import time
import rsa
import base64

print('Loading...')

class Transaction:
    def __init__(self, amount: float, payer: str, receiver: str):
        self.amount = amount
        self.payer = payer 
        self.receiver = receiver 
        self.signature = None

    def sign_transaction(self, private_key):
        transaction_string = self.__str__()
        self.signature = base64.b64encode(rsa.sign(transaction_string.encode(), private_key, 'SHA-256')).decode()

    def verify_signature(self):
        if not self.signature:
            return False
        try:
            public_key = rsa.PublicKey.load_pkcs1(self.payer.encode())
            signature = base64.b64decode(self.signature)
            rsa.verify(self.__str__().encode(), signature, public_key)
            return True
        except rsa.VerificationError:
            return False

    def __str__(self):

        return json.dumps({
            'amount': self.amount,
            'payer': self.payer,
            'receiver': self.receiver
        }, sort_keys=True)

class Wallet:
    def __init__(self):
        self.public_key, self.private_key = rsa.newkeys(2048)
    
    def send_money(self, amount: float, receiver_public_key: rsa.PublicKey, chain: 'Chain'):
        transaction = Transaction(amount, self.public_key.save_pkcs1().decode(), receiver_public_key.save_pkcs1().decode())
        transaction.sign_transaction(self.private_key)
        chain.add_transaction(transaction)
        print('Transaction sent successfully')
    
    def get_balance(self, chain: 'Chain'):
        return chain.get_balance(self.public_key.save_pkcs1().decode())

class Block:
    def __init__(self, prev_hash: str, transactions: list, timestamp: int = None):
        self.prev_hash = prev_hash
        self.transactions = transactions  # List of transactions
        self.timestamp = timestamp or int(time.time())
        self.nonce = 0
    
    def compute_hash(self):
        block_string = json.dumps({
            'prev_hash': self.prev_hash,
            'transactions': [json.loads(str(tx)) for tx in self.transactions],
            'timestamp': self.timestamp,
            'nonce': self.nonce
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
    
    def mine_block(self, difficulty: int):
        print('Mining...')
        prefix = '0' * difficulty
        while not self.compute_hash().startswith(prefix):
            self.nonce += 1

class Chain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.pending_transactions = []  # Pool of pending transactions
        self.difficulty = 4
        self.mining_reward = 50  # Reward for mining a block
    
    def create_genesis_block(self):
        genesis_key = rsa.newkeys(2048)[1]
        genesis_transaction = Transaction(100, "genesis_key", "satoshi_key")
        genesis_transaction.signature = base64.b64encode(rsa.sign(genesis_transaction.__str__().encode(), genesis_key, 'SHA-256')).decode()
        return Block("0", [genesis_transaction])  # Genesis block with a single transaction
    
    def get_last_block(self):
        return self.chain[-1]
    
    def add_transaction(self, transaction: Transaction):
        if not transaction.verify_signature():
            raise ValueError("Invalid transaction signature")
        self.pending_transactions.append(transaction)
        print('Transaction added to the pool')

    def mine_pending_transactions(self, miner_wallet: Wallet):
        if not self.pending_transactions:
            print('No transactions to mine')
            return
        
        # Create a reward transaction for the miner
        reward_transaction = Transaction(self.mining_reward, "MINING_REWARD", miner_wallet.public_key.save_pkcs1().decode())
        self.pending_transactions.append(reward_transaction)
        
        # Create a new block with all pending transactions
        new_block = Block(self.get_last_block().compute_hash(), self.pending_transactions)
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)
        
        # Clear the pending transactions after mining
        self.pending_transactions = []
        print('Block mined and added to the blockchain')

    def get_balance(self, public_key_pem: str):
        balance = 0
        for block in self.chain:
            for transaction in block.transactions:
                if transaction.payer == public_key_pem:
                    balance -= transaction.amount
                if transaction.receiver == public_key_pem:
                    balance += transaction.amount
        return balance


# Usage
chain = Chain()

satoshi = Wallet()
ts1 = Wallet()
ts2 = Wallet()

# Satoshi sends 10 coins to ts1
satoshi.send_money(10, ts1.public_key, chain)

# Check balances before mining
print(f"Ts1 Balance (before mining): {ts1.get_balance(chain)}")
print(f"Satoshi Balance (before mining): {satoshi.get_balance(chain)}")

# Mine the pending transactions
chain.mine_pending_transactions(satoshi)

'''
import hashlib
import time

class Block:
    def __init__(self, timestamp, data, previous_hash):
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()
    
    def calculate_hash(self):
        block_string = f"{self.timestamp}{self.data}{self.previous_hash}"
        return hashlib.sha256(block_string.encode('utf-8')).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
    
    def create_genesis_block(self):
        return Block(time.time(), "Genesis Block", "0")
    
    def get_latest_block(self):
        return self.chain[-1]
    
    def add_block(self, new_block):
        new_block.previous_hash = self.get_latest_block().hash
        new_block.hash = new_block.calculate_hash()
        self.chain.append(new_block)
    
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


amjkcoin.add_block(Block(time.time(), {"amount": 4}, amjkcoin.get_latest_block().hash))
amjkcoin.add_block(Block(time.time(), {"amount": 34}, amjkcoin.get_latest_block().hash))


for block in amjkcoin.chain:
    print(f"Timestamp: {block.timestamp}, Data: {block.data}, Hash: {block.hash}, Previous Hash: {block.previous_hash}")

print(amjkcoin.check_chain_validity())