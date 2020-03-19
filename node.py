import block
import wallet
from blockchain import BlockChain

class node:
	def __init__(self, id, ip, port, wallet):
		self.chain = None

		self.NBC = 0
		self.id = id
		self.wallet = wallet
		self.ip = ip
		self.port = port
		self.chain = BlockChain()
		self.ring = []   #here we store information for every node, as its id, its address (ip:port) its public key and its balance
		self.current_node_count = len(self.ring)

	def get_hosts(self):
		return [(ip, port) for ip, port, _, _ in self.ring]

	# def create_new_block():



	# def create_transaction(sender, receiver, signature):
	# 	#remember to broadcast it


	# def broadcast_transaction():


	# def validdate_transaction():
	# 	#use of signature and NBCs balance


	# def add_transaction_to_block():
	# 	#if enough transactions  mine



	# def mine_block():



	# def broadcast_block():


		

	# def valid_proof(.., difficulty=MINING_DIFFICULTY):




	# #concencus functions

	# def valid_chain(self, chain):
	# 	#check for the longer chain accroose all nodes


	# def resolve_conflicts(self):
	# 	#resolve correct chain



