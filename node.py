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
        self.current_block = []		# TODO: Imporve this
        # here we store information for every node, as its id, its (ip:port) its public key and its balance
        self.ring = []
        self.current_node_count = len(self.ring)

    def get_suffisient_UTXOS(self, ammount):
        UTXOS = list(filter(lambda x: x[2] == self.wallet.address, self.ring))[
            0][3]
        t_ids = []
        balance = 0
        for id in UTXOS:
            if balance >= ammount:
                break
            balance += UTXOS[id][1]
            t_ids.append(id)
        return t_ids

    def get_UTXO(self):
        return list(filter(lambda x: x[2] == self.wallet.address, self.ring))[0][3]

    def get_UTXOS(self):
        return list(map(lambda x: x[3], self.ring))

    def balance(self, address):
        UTXOS = list(filter(lambda x: x[2] == address, self.ring))[0][3]
        return sum(map(lambda x: x[1], UTXOS.values()))

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

    # def create_new_block():

    # def create_transaction(sender, receiver, signature):
    # 	#remember to broadcast it

    # def broadcast_transaction():

    def validdate_transaction(self, t):
        # use of signature and NBCs balance
        current_balance = 0
        if(t.receiver_address == t.sender_address):
            print('Cannot send transaction to self')
            return False

        UTXOS_sed = list(
            filter(lambda x: x[2] == t.sender_address, self.ring))[0][3]
        for id in t.transaction_inputs:
            if id in UTXOS_sed:
                current_balance += UTXOS_sed[id][1]
            else:
                print('Input not found')
                return False
        if current_balance < t.amount:
            print('Amount not found')
            return False
        for id in t.transaction_inputs:
            del UTXOS_sed[id]
        UTXOS_sed[t.transaction_id] = (
            t.sender_address, t.transaction_outputs[1]['amount'])
        UTXOS_reciv = list(
            filter(lambda x: x[2] == t.receiver_address, self.ring))[0][3]
        UTXOS_reciv[t.transaction_id] = (t.receiver_address, t.amount)
        return True

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

