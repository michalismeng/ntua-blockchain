import blockchain
import time
import settings
from transaction import Transaction
from Crypto.Hash import SHA
import jsonpickle as jp
from blockchain_subjects import consensusS


class Block:
	#TODO: remove nonce from constructor
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
		# TODO: remove this line
		self.current_hash = str(self.__myHash__().hexdigest())
	
	def transaction_ids(self):
		return [transaction.transaction_id for transaction in self.transactions]

	def verify_block(self, last_block, consensus_mode = False):
		if str(self.__myHash__().hexdigest()) != self.current_hash:
			return False

		#TODO: uncomment to check nonce
		# if not(self.current_hash.startswith(settings.difficulty * '0')):
		# 	return False

		# print(self.previous_hash)
		# print(last_block.current_hash)
		# print(self.index)
		# print(last_block.index + 1)
		
		if self.previous_hash == last_block.current_hash and self.index == last_block.index + 1:
			return True

		print('Invalid block.')
		if self.index > last_block.index and not(consensus_mode):
			print('Consensus is needed.')
			consensusS.on_next(0)

		return False

	def set_nonce(self, nonce):
		self.nonce = nonce

	def is_full(self):
		return len(self.transactions) >= settings.capacity
	
	def stringify(self):
	    return '({}, {}, {})'.format(self.index, self.previous_hash, self.current_hash)
		