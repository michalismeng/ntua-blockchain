import block
import wallet
from blockchain import BlockChain
import settings
import threading
from collections import deque
from copy import deepcopy

class node:
    def __init__(self, id, ip, port, wallet):
        self.chain = None

        self.NBC = 0
        self.id = int(id)
        self.wallet = wallet
        self.ip = ip
        self.port = port
        self.chain = BlockChain()
        self.lock = threading.Lock()
        self.current_block = []		# TODO: Imporve this
        # here we store information for every node, as its id, its (ip:port) its public key and its UTXOS (sender address: receiver id, amount)
        self.ring = []
        self.current_node_count = len(self.ring)

    def get_suffisient_UTXOS(self, ammount):
        UTXOS = self.get_node_UTXOS(self.id)
        t_ids = []
        balance = 0
        for id in UTXOS:
            if balance >= ammount:
                break
            balance += UTXOS[id][1]
            t_ids.append(id)
        return t_ids, balance

    def get_node_UTXOS(self, id):
        _, _, _, utxos = self.ring[id]
        return utxos

    def get_all_UTXOS(self):
        return [utxos for _, _, _, utxos in self.ring]

    def get_node_balance(self, id):
        UTXOS = self.get_node_UTXOS(id)
        return sum([amount for _, amount in UTXOS.values()])

    def set_ring(self, ring):
        self.ring = ring

    def get_hosts(self):
        return [(ip, port) for ip, port, _, _ in self.ring]

    def address_to_host(self, address):
        match = [(ip, port)
                 for ip, port, pkey, _ in self.ring if pkey == address]
        if len(match) > 0:
            return match[0]
        return 0

    def address_to_id(self, address):
        match = [id for id, (_, _, pkey, _) in enumerate(
            self.ring) if pkey == address]
        return match[0]

    # def create_new_block():

    # def create_transaction(sender, receiver, signature):
    # 	#remember to broadcast it

    # def broadcast_transaction():

    def validdate_transaction(self, t):
        current_balance = 0
        if(t.receiver_address == t.sender_address):
            print('Cannot send transaction to self')
            return False

        UTXOS_sender = self.get_node_UTXOS(
            self.address_to_id(t.sender_address))
        UTXOS_receiver = self.get_node_UTXOS(
            self.address_to_id(t.receiver_address))

        for id in t.transaction_inputs:
            if id in UTXOS_sender:
                current_balance += UTXOS_sender[id][1]
            else:
                print('Input not found')
                return False

        if current_balance < t.amount:
            print('Amount not found')
            return False

        for id in t.transaction_inputs:
            del UTXOS_sender[id]

        UTXOS_sender[t.transaction_id] = (
            t.sender_address, t.transaction_outputs[1]['amount'])
        UTXOS_receiver[t.transaction_id] = (
            t.receiver_address, t.transaction_outputs[0]['amount'])

        return True

    def add_transaction_to_block(self, t):
        self.current_block.append(t)
        # self.lock.acquire()
        # if len(self.current_block) >= settings.capacity:
        #     temp_block = deepcopy(self.current_block[:settings.capacity])
        #     print(self.chain.chain[-1])
        #     new_block = block.Block(self.chain.chain[-1].index, self.chain.chain[-1].current_hash)
        #     print(new_block)
        #     while not new_block.is_full():
        #         new_block.add_transaction(temp_block.pop())
        #     new_block.set_nonce(self.mine_block(new_block))
        #     self.chain.add_block(new_block)
        # self.lock.release()
        # TODO:mine
        # if enough transactions  mine

    def mine_block(self, b):
        return 0

    # def broadcast_block():

    # def valid_proof(.., difficulty=MINING_DIFFICULTY):

    # #concencus functions

    # def valid_chain(self, chain):
    # 	#check for the longer chain accroose all nodes
    # def resolve_conflicts(self):
    # 	#resolve correct chain
