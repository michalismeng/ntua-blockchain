import blockchain
import time
from Crypto.Hash import SHA


class Block:
	def __init__(self, index, previous_hash):
		self.index = index
		self.timestamp = time.time()
		self.transactions = []
		self.nonce = None
		self.previous_hash = previous_hash
		self.current_hash = self.__myHash__()

	
	def __myHash__(self):
		hashString = "%s%s%s" % (self.index, self.previous_hash.hexdigest(), self.nonce) 
		return SHA.new(hashString.encode())

	# transaction and block capacity must have already been validated
	def add_transaction(self, transaction):
		self.transactions.append(transaction)