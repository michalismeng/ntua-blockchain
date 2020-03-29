from random import randint

class Miner: 
      
    def __init__(self):
        self.running = False
      
    def terminate(self): 
        self.running = False

    def mine(self,block,id):
        self.running = True

        nonce = (randint(0, 4294967295) * id) % 4294967295
        block.seal_block(nonce)

        while self.running and not(block.is_block_gold()):
            nonce = (nonce+1) % 4294967295
            block.seal_block(nonce)

        self.running = False