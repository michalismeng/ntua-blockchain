import block
import settings
import jsonpickle as jp
from copy import deepcopy
from Crypto.Hash import SHA
import utils

class BlockChain:

    def __init__(self):
        self.chain = []             # list of blocks in the blockchain
        self.UTXO_history = []      # UTXOS for every block
        self.common_index = 1       # marks the index until which all nodes agree on the blockchain (actually one past that index)
    
    def get_recent_UTXOS(self):
        return self.UTXO_history[-1]

    def add_block(self,b,utxos):
        self.chain.append(b)
        self.UTXO_history.append(deepcopy(utxos))

    def get_last_block(self):
        return self.chain[-1]

    def in_genesis_state(self):
        return len(self.chain) == 0

    def get_block_indexes(self):
        return [block.index for block in self.chain]
    
    def chain_to_hashes(self):
        return [block.current_hash for block in self.chain]

    def get_global_common_index(self, all_hashes):
        return min([utils.get_max_common_prefix_length(hash_chain, self.chain_to_hashes()[self.common_index:]) for hash_chain in all_hashes])

    def set_max_common_index(self, index):
        self.common_index = index