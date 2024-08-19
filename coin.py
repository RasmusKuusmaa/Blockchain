import hashlib
import json
import time
import rsa

print('Loading...')
class Transaction:
    def __init__(self, amount: float, payer: str, receiver: str):
        self.amount = amount
        self.payer = payer
        self.receiver = receiver
    
    def __str__(self):
        return json.dumps(self.__dict__)

class Block:
    def __init__(self, prev_hash: str, transaction: Transaction, timestamp: int = None):
        self.prev_hash = prev_hash
        self.transaction = transaction
        self.timestamp = timestamp or int(time.time())
        self.nonce = 0
    
    def compute_hash(self):
        block_string = json.dumps({
            'prev_hash': self.prev_hash,
            'transaction': json.loads(str(self.transaction)),
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
        self.difficulty = 4
    
    def create_genesis_block(self):
        return Block("0", Transaction(100, "genesis", "satoshi"))
    
    def get_last_block(self):
        return self.chain[-1]
    
    def add_block(self, transaction: Transaction):
        new_block = Block(self.get_last_block().compute_hash(), transaction)
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)

class Wallet:
    def __init__(self):
        self.public_key, self.private_key = rsa.newkeys(2048)
    
    def send_money(self, amount: float, receiver_public_key: rsa.PublicKey):
        transaction = Transaction(amount, str(self.public_key), str(receiver_public_key))
        signature = rsa.sign(transaction.__str__().encode(), self.private_key, 'SHA-256')
        
   
        global chain
        chain.add_block(transaction)
        print('sending')



#Usage

chain = Chain()


satoshi = Wallet()
ts1 = Wallet()
ts2 = Wallet()


satoshi.send_money(10, ts1.public_key)