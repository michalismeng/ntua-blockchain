import block
import settings

class BlockChain:

    def __init__(self):
        self.chain = []
    
    def add_transaction(self,t):
        if not(self.chain[-1].is_full()):
            self.chain[-1].add_transaction(t)
    
    def add_block(self,b):
        self.chain.append(b)