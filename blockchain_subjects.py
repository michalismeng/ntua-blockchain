from rx.subject import Subject, ReplaySubject

# node count subject - used only by the bootstrap node
node_countS = ReplaySubject()

# node subject
nodeS = Subject()

# transaction subject
tsxS = Subject()

# block subject
blcS = Subject()

# ring subject
ringS = Subject()

# command subject
commandS = Subject()

# genesis block subject
genesisS = Subject()

# my transaction subject
mytsxS = Subject()

# consensus subject
consensusS = Subject()

consensusSucceededS = Subject()

# miner subject
minerS = Subject()