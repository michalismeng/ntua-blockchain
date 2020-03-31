import block
import wallet
from blockchain import BlockChain
import settings
import threading
from collections import deque
from copy import deepcopy
from random import randint
from miner import Miner
from blockchain_subjects import minerS
import utils

class node:
    def __init__(self, id, ip, port, wallet):

        self.id = int(id)
        self.wallet = wallet
        self.ip = ip
        self.port = port
        self.chain = BlockChain()
        self.lock = threading.Lock()
        self.current_block = []
        self.miner = Miner()
        # here we store information for every node, its (ip:port) its public key and its UTXOS ({ sender address: receiver id, amount })
        self.ring = []
        self.commands_script = []
        self.current_node_count = len(self.ring)

    def get_suffisient_UTXOS(self, ammount):
        UTXOS = self.get_node_UTXOS(self.id)
        t_ids = []
        balance = 0
        for id in [k for k, _ in sorted(UTXOS.items(), key=lambda item: item[1][1])]:
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

    def set_all_utxos(self, UTXOS):
        self.ring = [(ring_entry[0], ring_entry[1], ring_entry[2], deepcopy(UTXO))
                     for ring_entry, UTXO in zip(self.ring, UTXOS)]

    def get_node_balance(self, id):
        UTXOS = self.get_node_UTXOS(id)
        return sum([amount for _, amount in UTXOS.values()])

    def set_ring(self, ring):
        self.ring = ring

    def set_current_block(self, transactions):
        self.current_block = transactions

    def get_pending_transactions(self):
        return [t.transaction_id for t in self.current_block]

    def get_host_by_id(self, id):
        return (self.ring[id][0], self.ring[id][1])

    def get_hosts(self):
        return [(ip, port) for ip, port, _, _ in self.ring]

    def get_other_hosts(self):
        return [(ip, port) for ind, (ip, port, _, _) in enumerate(self.ring) if ind != self.id]

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

    def validate_transaction(self, t, UTXOS, verbose=False):
        current_balance = 0
        if(t.receiver_address == t.sender_address):
            if verbose:
                print('Cannot send transaction to self')
            return None

        UTXOS_sender = UTXOS[
            self.address_to_id(t.sender_address)]
        UTXOS_receiver = UTXOS[
            self.address_to_id(t.receiver_address)]

        for id in t.transaction_inputs:
            if id in UTXOS_sender:
                current_balance += UTXOS_sender[id][1]
            else:
                if verbose:
                    print('Input not found',t.stringify(self))
                return None

        if current_balance < t.amount:
            if verbose:
                print('Amount not found')
            return None

        for id in t.transaction_inputs:
            del UTXOS_sender[id]

        UTXOS_sender[t.transaction_id] = (
            t.sender_address, t.transaction_outputs[1]['amount'])
        UTXOS_receiver[t.transaction_id] = (
            t.receiver_address, t.transaction_outputs[0]['amount'])

        return UTXOS

    def validate_transactions(self, ts, initial_utxos):
        temp_utxos = deepcopy(initial_utxos)
        valid_transactions = []

        for t in ts:
            new_utxos = self.validate_transaction(t, temp_utxos)
            if new_utxos != None:
                valid_transactions.append(t)
                temp_utxos = new_utxos

        return valid_transactions, temp_utxos

    def validate_block(self, new_block, UTXOS):
        valid_transactions, new_utxos = self.validate_transactions(new_block.transactions, UTXOS)
        success = len(valid_transactions) == len(new_block.transactions)

        # if all transactions of the block are valid => update utxos
        # else failure

        if success:
            return new_utxos
        else:
            return None

    def add_transaction_to_block(self, t):
        self.current_block.append(t)

    def look_for_ore_block(self):
        index = self.chain.get_last_block().index+1
        hs = self.chain.get_last_block().current_hash
        b = block.Block(index, hs, 0)
        b.transactions = self.current_block[:settings.capacity]
        return b

    def verify_chain(self, blocks, index):
        # temp_blocks = zip([last_block] + blocks[:-1], blocks)
        temp_blocks = [self.chain.chain[index - 1]] + blocks

        for i in range(len(temp_blocks) - 1):
            if not(temp_blocks[i + 1].verify_block(temp_blocks[i], True)):
                return False

        return True

    def validate_chain(self, blocks, index): 
        hash_blocks = [b.current_hash for b in blocks]
        hash_my_blocks = [b.current_hash for b in self.chain.chain[index:]]
        max_common_index = utils.get_max_common_prefix_length(hash_blocks, hash_my_blocks)

        temp_UTXOS = [self.chain.UTXO_history[index+max_common_index-1]]
        transactions = set()

        for block in blocks[max_common_index:]:
            new_UTXOS = self.validate_block(block, temp_UTXOS[-1])
            if new_UTXOS == None:
                return None
                
            transactions.update([t.transaction_id for t in block.transactions])
            temp_UTXOS.append(new_UTXOS)

        return temp_UTXOS[1:], index + max_common_index, transactions
