import block
import settings
import jsonpickle as jp
from copy import deepcopy
from Crypto.Hash import SHA

class BlockChain:

    def __init__(self):
        self.chain = []
        self.UTXOS = []
    
    def set_utxos(self, utxos):
        self.UTXOS = utxos
        
    def add_block(self,b):
        self.chain.append(b)

    def get_last_block(self):
        return self.chain[-1]

    def in_genesis_state(self):
        return len(self.chain) == 0

    def get_block_indexes(self):
        return [block.index for block in self.chain]
    
    def verify_block(self,b):
        if b.previous_hash == self.chain[-1].current_hash and b.index == self.chain[-1].index+1:
            return True

        print('Invalid block.')
        if b.index > self.chain[-1].index:
            print('Consensus is needed.')
            #do_consensus
            pass

        #TODO: nonce check
        return False
        
        
