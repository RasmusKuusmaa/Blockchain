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
    def __init__(self, timestamp, data, previousHash):
        self.timestamp = timestamp
        self.data = data
        self.previousHash = previousHash
        self.hash = self.calculateHash()
    
    def calculateHash(self):
        block_string = str(self.timestamp) + str(self.data) + str(self.previousHash)
        block_hash = hashlib.sha256(block_string.encode('utf-8')).hexdigest()
        return block_hash

class Blockchain:
    def __init__(self):
        self.chain = [self.createGenesisBlock()]
    
    def createGenesisBlock(self):
        return Block(time.time(), "Genesis Block", "0")
    
    def getLatestBlock(self):
        return self.chain[-1]
    
    def addBlock(self, newBlock):
        newBlock.previousHash = self.getLatestBlock().hash
        newBlock.hash = newBlock.calculateHash()
        self.chain.append(newBlock)

# Instantiate Blockchain
amjkcoin = Blockchain()

# Add blocks
amjkcoin.addBlock(Block(time.time(), {"amount": 4}, amjkcoin.getLatestBlock().hash))
amjkcoin.addBlock(Block(time.time(), {"amount": 34}, amjkcoin.getLatestBlock().hash))

# Print the blockchain
for block in amjkcoin.chain:
    print(f"Timestamp: {block.timestamp}, Data: {block.data}, Hash: {block.hash}, Previous Hash: {block.previousHash}")
