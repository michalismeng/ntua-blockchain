import time
import settings
from transaction import Transaction
from Crypto.Hash import SHA
import jsonpickle as jp
from blockchain_subjects import consensusS


class Block:
	def __init__(self, index, previous_hash, nonce = None):
		self.index = int(index)
		self.timestamp = time.time()
		self.transactions = []
		self.nonce = nonce
		self.previous_hash = previous_hash
		self.current_hash = str(self.__myHash__().hexdigest())

	def seal_block(self,nonce):
		self.timestamp = time.time()
		self.nonce = nonce
		self.current_hash = str(self.__myHash__().hexdigest())

	def is_block_gold(self):
		return self.current_hash.startswith('0'*settings.difficulty)

	@staticmethod
	def genesis(bootstrap_address):
		b = Block(0, 1, 0)
		b.add_transaction(Transaction(0, bootstrap_address, settings.N * 100, settings.N * 100, []))
		return b
	
	def __myHash__(self):
		hashString = jp.encode((self.index,self.timestamp,[t.transaction_id for t in self.transactions],self.nonce,self.previous_hash))
		return SHA.new(hashString.encode())

	def add_transaction(self, transaction):
		self.transactions.append(transaction)
	
	def transaction_ids(self):
		return [transaction.transaction_id for transaction in self.transactions]

	# verify a block and request consensus if needed
	def verify_block(self, last_block, consensus_mode = False):
		if str(self.__myHash__().hexdigest()) != self.current_hash:
			return False

		if not(self.current_hash.startswith(settings.difficulty * '0')):
			return False

		if self.previous_hash == last_block.current_hash and self.index == last_block.index + 1:
			return True

		if self.index > last_block.index and not(consensus_mode):
			print('Consensus is needed.')
			consensusS.on_next(0)

		print('Invalid block.')
		return False

	def set_nonce(self, nonce):
		self.nonce = nonce

	def is_full(self):
		return len(self.transactions) >= settings.capacity
	
	def stringify(self):
	    return '({}, {}, {})'.format(self.index, self.previous_hash, self.current_hash)
		