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
        genesis_key = rsa.newkeys(2048)[1]
        genesis_transaction = Transaction(100, "genesis_key", "satoshi_key")
        genesis_transaction.signature = base64.b64encode(rsa.sign(genesis_transaction.__str__().encode(), genesis_key, 'SHA-256')).decode()
        return Block("0", genesis_transaction)
    
    def get_last_block(self):
        return self.chain[-1]
    
    def add_block(self, transaction: Transaction):
        if not transaction.verify_signature():
            raise ValueError("Signature no bueno")
        new_block = Block(self.get_last_block().compute_hash(), transaction)
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)

    def get_balance(self, public_key_pem: str):
        balance = 0
        for block in self.chain:
            transaction = block.transaction
            if transaction.payer == public_key_pem:
                balance -= transaction.amount
            if transaction.receiver == public_key_pem:
                balance += transaction.amount
        return balance
        

class Wallet:
    def __init__(self):
        self.public_key, self.private_key = rsa.newkeys(2048)
    
    def send_money(self, amount: float, receiver_public_key: rsa.PublicKey, chain: Chain):
        transaction = Transaction(amount, self.public_key.save_pkcs1().decode(), receiver_public_key.save_pkcs1().decode())
        transaction.sign_transaction(self.private_key)
        chain.add_block(transaction)
        print('Transaction sent successfully')
    def get_balance(self, chain: Chain):
        return chain.get_balance(self.public_key.save_pkcs1().decode())  


# Usage
chain = Chain()

satoshi = Wallet()
ts1 = Wallet()
ts2 = Wallet()

satoshi.send_money(10, ts1.public_key, chain)
print(ts1.get_balance(chain))
print("Blockchain:", chain.chain)
