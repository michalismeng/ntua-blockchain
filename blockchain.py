import block
import settings
from copy import deepcopy

class BlockChain:

    def __init__(self):
        self.chain = []
        self.UTXOS = []
    
    def add_transaction(self,t):
        if not(self.chain[-1].is_full()):
            self.chain[-1].add_transaction(t)
    
    def add_block(self,b):
        self.chain.append(b)

    def get_last_block(self):
        return self.chain[-1]

    def in_genesis_state(self):
        return len(self.chain) == 0

    def get_block_indexes(self):
        return [block.index for block in self.chain]
