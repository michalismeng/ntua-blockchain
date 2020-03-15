import block
import wallet

class node:
	def __init__(self, node_count, id, ip, port, wallet):
		self.chain = None

		self.NBC = 0
		self.current_node_count = node_count
		self.id = id
		self.wallet = wallet
		self.ip = ip
		self.port = port

		self.ring = []   #here we store information for every node, as its id, its address (ip:port) its public key and its balance 




	# def create_new_block():

	# def register_node_to_ring():
	# 	#add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
	# 	#bottstrap node informs all other nodes and gives the request node an id and 100 NBCs


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



