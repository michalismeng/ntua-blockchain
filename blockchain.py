import block
import settings
import jsonpickle as jp
from copy import deepcopy
from Crypto.Hash import SHA

class BlockChain:

    def __init__(self):
        self.chain = []
        self.UTXO_history = []
        self.common_index = 1
    
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

    def get_max_prefex_block_chain(self, blocks, index):
        for i, (my_block, other_block) in enumerate(zip(self.chain[index:], blocks)):
            if my_block.current_hash != other_block.current_hash:
                return i
        
        return len(self.chain[index:])

    def get_max_prefex_chain(self, hashes):

        for i, (my_hash, other_hash) in enumerate(zip(self.chain_to_hashes()[self.common_index:], hashes)):
            if my_hash != other_hash:
                return i

        return min(len(hashes), len(self.chain_to_hashes()[self.common_index:]))

    def set_max_common_index(self,hash_chains):
        self.common_index += min([self.get_max_prefex_chain(hash_chain) for hash_chain in hash_chains])