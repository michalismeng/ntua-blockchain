from rx.subject import Subject, ReplaySubject

# node count subject - used only by the bootstrap node
node_countS = ReplaySubject()

# node subject
nodeS = Subject()

# ring subject - emits when all nodes join the network
ringS = Subject()

# genesis block subject - emits when a genesis block is detected
genesisS = Subject()

# transaction subject
tsxS = Subject()

# my transactions subject - emits when the current node creates a transaction
mytsxS = Subject()

# block subject
blcS = Subject()

# myblock subject - emits when the miner thread finds a valid nonce
myblcS = Subject()

# consensus subject
consensusS = Subject()
consensusSucceededS = Subject()

# miner subject
minerS = Subject()

# command subject - manages endpoint commands
commandS = Subject()

# broadcast subject - all broadcasts that need to happen async use this subject
broadcastS = Subject()