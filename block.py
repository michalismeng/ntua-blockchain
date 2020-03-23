import blockchain
import time
import settings
from transaction import Transaction
from Crypto.Hash import SHA


class Block:
	def __init__(self, index, previous_hash, nonce = None):
		self.index = index
		self.timestamp = time.time()
		self.transactions = []
		self.nonce = nonce
		self.previous_hash = previous_hash
		self.current_hash = self.__myHash__()

	@staticmethod
	def genesis(bootstrap_address):
		b = Block(0,1,0)
		b.add_transaction(Transaction(0,bootstrap_address,settings.N*100,settings.N*100,[]))
		return b
	
	def __myHash__(self):
		hashString = "%s%s%s" % (self.index, self.previous_hash.hexdigest() if not(isinstance(self.previous_hash,int)) else str(self.previous_hash), self.nonce) 
		return SHA.new(hashString.encode())

	# transaction and block capacity must have already been validated
	def add_transaction(self, transaction):
		self.transactions.append(transaction)
	
	def set_nonce(self,nonce):
		self.nonce = nonce

	def is_full(self):
		return len(self.transactions) >= settings.capacity