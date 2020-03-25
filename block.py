import blockchain
import time
import settings
from transaction import Transaction
from Crypto.Hash import SHA
import jsonpickle as jp


class Block:
	def __init__(self, index, previous_hash, nonce = None):
		self.index = int(index)
		self.timestamp = time.time()
		self.transactions = []
		self.nonce = nonce
		self.previous_hash = previous_hash
		self.current_hash = str(self.__myHash__().hexdigest())

	@staticmethod
	def genesis(bootstrap_address):
		b = Block(0, 1, 0)
		b.add_transaction(Transaction(0, bootstrap_address, settings.N * 100, settings.N * 100, []))
		return b
	
	def __myHash__(self):
		hashString = jp.encode((self.index,self.timestamp,self.transactions,self.nonce,self.previous_hash))
		return SHA.new(hashString.encode())

	# transaction and block capacity must have already been validated
	def add_transaction(self, transaction):
		self.transactions.append(transaction)
	
	def transaction_ids(self):
		return [transaction.transaction_id for transaction in self.transactions]

	def set_nonce(self, nonce):
		self.nonce = nonce

	def is_full(self):
		return len(self.transactions) >= settings.capacity
	
	def stringify(self):
	    return '({}, {}, {})'.format(self.index, self.previous_hash, self.current_hash)
		