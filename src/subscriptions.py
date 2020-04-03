import rx
from rx import operators as ops
import rx.scheduler

from subscription_utils import do_broadcast_ring, check_correct_running_thread, do_bootstrap_transactions, create_transaction
from blockchain_subjects import nodeS, node_countS, ringS, genesisS, blcS, tsxS, mytsxS, commandS, consensusS, minerS, consensusSucceededS, myblcS, broadcastS
from cli import execute
import settings
from communication import broadcast,unicast
from threading import Thread
import utils
import threading
import time

# we define one common thread pool with one available thread to be used by all blockchain pipelines
# this way all pipelines run on the same thread => they are serialized and no concurrency control is required
blockchain_thread_pool = rx.scheduler.ThreadPoolScheduler(1)

# we also define such a thread pool for the miner
miner_thread_pool = rx.scheduler.ThreadPoolScheduler(1)

# and one for the external commands
cli_thread_pool = rx.scheduler.ThreadPoolScheduler(1)

# hacky global timestamp
block_mining_time_stamp = 0

def set_block_mining_time_stamp():
    global block_mining_time_stamp
    block_mining_time_stamp = time.time()

#
#   MAIN PROGRAM PIPELINES
#

# control miner execution
def miner_operator():
    return rx.pipe(
        ops.filter(lambda o: len(o['node'].current_block) >= settings.capacity and not(o['node'].miner.running)),
        ops.do_action(lambda o: print('starting Miner')),
        ops.do_action(lambda o: o['node'].miner.set_running()),
        ops.do_action(lambda o: minerS.on_next(0))
    )

rx.combine_latest(
    nodeS,
    minerS
).pipe(
    # use miner thread
    ops.observe_on(miner_thread_pool),
    # ops.do_action(lambda o: print(threading.currentThread().name)),

    ops.do_action(lambda o: print('Entering miner')),
    ops.map(lambda nc: {'node': nc[0]}),

    # get 'capacity' transaction from transaction pool
    ops.map(lambda o: {'node':o['node'], 'block':o['node'].look_for_ore_block()}),
    ops.do_action(lambda o: set_block_mining_time_stamp()),
    ops.do_action(lambda o: print('Har Har Har found the ore')),

    # mine the block
    ops.do_action(lambda o: o['node'].miner.mine(o['block'],o['node'].id)),

    ops.do_action(lambda o: print('I see something in me rock')),

    # stop the pipeline if the nonce is not good (aka the miner was interrupted)
    ops.filter(lambda o: o['block'].is_block_gold()),
    ops.do_action(lambda o: print('It is GOLD I tell ya')),

    # if the nonce found is OK, emit the block
    ops.do_action(lambda o: myblcS.on_next(o['block'])),    
    ops.do_action(lambda o: print('Ya\'ll got me gold!')),
).subscribe()

# node pipeline - the first to be executed
nodeS.pipe(
    # use blockchain thread as every other pipeline
    ops.observe_on(blockchain_thread_pool),

    ops.do_action(lambda miner: print("Created miner with id: ", miner.id))
).subscribe()

# node count pipeline - used only by the bootstrap node
rx.combine_latest(
    nodeS,
    node_countS
).pipe(
    ops.observe_on(blockchain_thread_pool),
    ops.map(lambda nc: {'boot_node': nc[0], 'count': nc[1]}),

    # broadcast the ring only when N nodes have joined the network
    ops.filter(lambda o: o['count'] == settings.N - 1),
    ops.do_action(lambda o: do_broadcast_ring(o['boot_node']))
).subscribe()

# ring pipeline
rx.zip(
    nodeS,
    ringS,
).pipe(
    ops.observe_on(blockchain_thread_pool),
    ops.do_action(lambda _: check_correct_running_thread()),

    # Set the node's ring upon receiving one
    ops.do_action(lambda x: x[0].set_ring(x[1])),
    ops.do_action(lambda x: print('Current ring: ', x[0].get_hosts())),
).subscribe()

# genesis block pipeline - only the bootstrap node should execute this pipeline
rx.combine_latest(
    nodeS,
    genesisS
).pipe(
    ops.observe_on(blockchain_thread_pool),
    ops.do_action(lambda _: check_correct_running_thread()),

    # run pipeline for bootstrap node only
    ops.filter(lambda ng: ng[0].id == 0),

    # when the genesis block is received, the bootstrap node must execute the initialization transactions
    ops.do_action(lambda ng: do_bootstrap_transactions(ng[0]))
).subscribe()

# pipeline to detect genesis block
rx.combine_latest(
    nodeS,
    blcS
).pipe(
    ops.observe_on(blockchain_thread_pool),
    ops.do_action(lambda _: check_correct_running_thread()),

    ops.map(lambda nb: {'node': nb[0], 'bl': nb[1]}),

    # check if this is a genesis block
    ops.filter(lambda o: o['bl'].previous_hash == 1),

    # check that this is the first (and only) genesis block to arrive
    ops.filter(lambda o: o['node'].chain.in_genesis_state()),
    ops.map(lambda o: {'node': o['node'], 'bl': o['bl'], 'tsx': o['bl'].transactions[0]}),

    # add genesis block to blockchain and configure utxos
    ops.do_action(lambda o: o['node'].chain.add_block(o['bl'],
        [{o['tsx'].transaction_id: (o['node'].ring[0][2], 100 * settings.N)}] + [{} for i in range(settings.N-1)])),
    ops.do_action(lambda o: o['node'].set_all_utxos(o['node'].chain.get_recent_UTXOS())),

    ops.do_action(lambda o: print('Added genesis block to blockchain')),

    # notify genesis block is received and allow transactions to happen
    ops.do_action(lambda o: genesisS.on_next(0))
).subscribe()

# pipeline for normal block
rx.combine_latest(
    nodeS,
    blcS,
).pipe(
    ops.observe_on(blockchain_thread_pool),
    ops.do_action(lambda _: check_correct_running_thread()),

    ops.map(lambda nl: {'node': nl[0], 'bl': nl[1]}),

    # check that this is not a genesis block
    ops.filter(lambda o: o['bl'].previous_hash != 1),

    # verify block signature -- this may lead to consensus being called
    ops.filter(lambda o: o['bl'].verify_block(o['node'].chain.get_last_block())),

    # validate block transactions
    ops.map(lambda o: {'node': o['node'], 'bl': o['bl'], 'utxos': o['node'].validate_block(o['bl'],o['node'].chain.get_recent_UTXOS())}),
    ops.filter(lambda o: o['utxos'] != None),

    # kill miner since a valid block just arrived
    ops.do_action(lambda o: o['node'].miner.terminate()),
    
    # add block to the blockchain and update the curent state
    ops.do_action(lambda o: o['node'].chain.add_block(o['bl'],o['utxos'])),
    ops.map(lambda o: {'node': o['node'], 'bl': o['bl'], 'new_state':o['node'].validate_transactions(o['node'].current_block, o['node'].chain.get_recent_UTXOS())}),
    ops.do_action(lambda o: o['node'].set_current_block(o['new_state'][0])),
    ops.do_action(lambda o: o['node'].set_all_utxos(o['new_state'][1])),

    ops.do_action(lambda o: print('Received block: ', o['bl'].stringify())),

    # keep timestamp of block validation
    ops.do_action(lambda o: settings.block_validation_time_stamps.append((time.time(),o['bl'].index,o['bl'].current_hash))),

    # activate miner if needed
    miner_operator()
).subscribe()

# pipeline for my block -- execution is the same as for a normal block. This pipeline is used for blocks generated by this node
rx.combine_latest(
    nodeS,
    myblcS,
).pipe(
    ops.observe_on(blockchain_thread_pool),
    ops.do_action(lambda _: check_correct_running_thread()),

    ops.map(lambda nl: {'node': nl[0], 'bl': nl[1]}),

    # verify - validate - update state as before        # TODO: Refactor and use rxpy operators
    ops.filter(lambda o: o['bl'].verify_block(o['node'].chain.get_last_block())),
    ops.map(lambda o: {'node': o['node'], 'bl': o['bl'], 'utxos': o['node'].validate_block(o['bl'],o['node'].chain.get_recent_UTXOS())}),
    ops.filter(lambda o: o['utxos'] != None),

    ops.do_action(lambda o: o['node'].chain.add_block(o['bl'],o['utxos'])),
    ops.map(lambda o: {'node': o['node'], 'bl': o['bl'], 'new_state':o['node'].validate_transactions(o['node'].current_block, o['node'].chain.get_recent_UTXOS())}),
    ops.do_action(lambda o: o['node'].set_current_block(o['new_state'][0])),
    ops.do_action(lambda o: o['node'].set_all_utxos(o['new_state'][1])),

    ops.do_action(lambda o: print('Received block: ', o['bl'].stringify())),

    # keep timestamps
    ops.do_action(lambda o: settings.block_validation_time_stamps.append((time.time(),o['bl'].index,o['bl'].current_hash))),
    ops.do_action(lambda o: settings.block_mining_time_stamps.append((time.time() - block_mining_time_stamp,o['bl'].index,o['bl'].current_hash))),

    # kill miner
    ops.do_action(lambda o: o['node'].miner.terminate()),

    # notify every one -- this is not a blocking call
    ops.do_action(lambda o: broadcastS.on_next((o['node'].get_other_hosts(),'add-block', { 'block': o['bl'] }))),

    # restart miner with a new set of transactions if needed
    miner_operator()
).subscribe()

# pipeline for transactions - does not emit until genesis has arrived
rx.combine_latest(
    nodeS,
    genesisS,
    tsxS
).pipe(
    ops.observe_on(blockchain_thread_pool),
    ops.do_action(lambda _: check_correct_running_thread()),

    ops.map(lambda nl: {'node': nl[0], 'tx': nl[2], 'utxos': nl[0].get_all_UTXOS()}),

    # keep timestamp for experiments
    ops.do_action(lambda o: settings.transaction_time_stamps.append((time.time(),o['tx'].transaction_id))),

    # verify transaction signature
    ops.filter(lambda o: o['tx'].verify_transaction()),

    # validate transaction based on the current set of utxos
    ops.map(lambda o: {'node': o['node'], 'tx': o['tx'], 'new_utxos': o['node'].validate_transaction(o['tx'], o['utxos'], True)}),
    ops.filter(lambda o: o['new_utxos'] != None),

    # if the transaction is valid, update the current state
    ops.do_action(lambda o: o['node'].set_all_utxos(o['new_utxos'])),
    ops.do_action(lambda o: o['node'].add_transaction_to_block(o['tx'])),

    ops.do_action(lambda o: print('Received transaction: ', o['tx'].stringify(o['node']))),
    ops.do_action(lambda o: settings.v_transactions.append((time.time(),o['tx'].transaction_id))),

    # restart the miner if necessary
    miner_operator()
).subscribe()

# pipeline for my transactions -- execution is the same as for a normal transaction. This pipeline is used for transactions generated by this node
rx.combine_latest(
    nodeS,
    mytsxS
).pipe(
    ops.observe_on(blockchain_thread_pool),
    ops.do_action(lambda _: check_correct_running_thread()),

    ops.map(lambda nl: {'node': nl[0], 'target': nl[1][0], 'amount': nl[1][1]}),

    # create transaction
    ops.map(lambda o: {'node': o['node'], 'tx': create_transaction(o['node'],o['target'],o['amount']), 'utxos': o['node'].get_all_UTXOS()}),

    # keep timestamp for experiments
    ops.do_action(lambda o: settings.transaction_time_stamps.append((time.time(),o['tx'].transaction_id))),

    # verify - validate - update as before (only validation is required to update utxos) # TODO: refactor with rxpy operators
    ops.filter(lambda o: o['tx'].verify_transaction()),

    ops.map(lambda o: {'node': o['node'], 'tx': o['tx'], 'new_utxos': o['node'].validate_transaction(o['tx'], o['utxos'], True)}),
    ops.filter(lambda o: o['new_utxos'] != None),

    ops.do_action(lambda o: o['node'].set_all_utxos(o['new_utxos'])),
    ops.do_action(lambda o: o['node'].add_transaction_to_block(o['tx'])),

    ops.do_action(lambda o: print('Received transaction: ', o['tx'].stringify(o['node']))),
    ops.do_action(lambda o: settings.v_transactions.append((time.time(),o['tx'].transaction_id))),

    # notify every one -- this is not a blocking call
    ops.do_action(lambda o: broadcastS.on_next((o['node'].get_other_hosts(), 'add-transaction', { 'transaction': o['tx'] }))),

    miner_operator()
).subscribe()

# utility functions not yet refactored

# called when a valid blockchain wsa found and we need to update our current blockchain
def consesus_succedeed(node, branch_index, utxo_history, chain, transactions):
    new_chain = node.chain.chain[:branch_index] + chain[-len(utxo_history):]
    new_utxos = node.chain.UTXO_history[:branch_index] +  utxo_history

    my_transactions = []

    for b in node.chain.chain[branch_index:]:
        my_transactions.extend(b.transactions)

    my_transactions.extend(node.current_block)

    # these transactions belonged to our old blockchain, so we should try and add them to our transaction pool
    transactions_to_add = [t for t in my_transactions if t.transaction_id not in transactions]

    # validate each transaction and keep only the ones that conform to the new blockchain
    valid_transactions, ring_utxos = node.validate_transactions(transactions_to_add, new_utxos[-1])

    # update the state
    node.set_current_block(valid_transactions)
    node.set_all_utxos(ring_utxos)
    
    node.chain.chain = new_chain
    node.chain.UTXO_history = new_utxos


def do_consensus(node, hashes):

    # sort all chains based on their length while keeping the id of the node 
    ids_hashes = sorted(hashes, reverse = True, key = lambda x: len(x['hashes']))

    # starting with the node with the longest chain, request his blocks and try to reach consensus
    for item in ids_hashes:
        id = item['id']
        hashes = item['hashes']
        host = node.get_host_by_id(id)

        # find the max common subchain with the node under consideration (this may differ from the previous global common chain we calculated)
        new_index = node.chain.common_index + utils.get_max_common_prefix_length(hashes, node.chain.chain_to_hashes()[node.chain.common_index:])

        print('branch for node {} detected at index: {}'.format(id, new_index))

        # request the block chain, after the specified index
        block_chain = unicast(host, 'request-chain', { 'index': new_index })

        if not(node.verify_chain(block_chain, new_index)):
            print('Consensus chain is not verified')
            return False

        utxo_history, branch_index, transactions = node.validate_chain(block_chain, new_index)
        if utxo_history != None:
            # this is a blocking call
            consensusSucceededS.on_next((branch_index, utxo_history, block_chain, transactions, ids_hashes))

            print('consesnus reached based on info by node ' + str(id))
            return True

    print('Could not achieve consensus')
    return False

rx.combine_latest(
    nodeS,
    consensusS
).pipe(
    # this subscription is called immediately when called -- this is a blocking call
    ops.observe_on(rx.scheduler.ImmediateScheduler()),
    ops.do_action(lambda _: check_correct_running_thread()),

    ops.map(lambda nl: {'node': nl[0]}),

    # kill miner for this operation
    ops.do_action(lambda o: o['node'].miner.terminate()),

    # request blockchain hashes from all nodes, after a certrain point in the blockchain (common_index) at which all nodes agree
    ops.map(lambda o: {'node': o['node'], 'results': broadcast(o['node'].get_other_hosts(), 'request-chain-hash', {'index': o['node'].chain.common_index })}),

    ops.do_action(lambda o: do_consensus(o['node'], o['results'])),

    miner_operator()
).subscribe()

rx.combine_latest(
    nodeS,
    consensusSucceededS
).pipe(
    # this subscription is called immediately when called -- this is a blocking call
    ops.observe_on(rx.scheduler.ImmediateScheduler()),
    ops.do_action(lambda _: check_correct_running_thread()),

    ops.map(lambda nc: {'node': nc[0], 'branch_index': nc[1][0], 'utxo_history': nc[1][1], 'block_chain': nc[1][2], 'transactions': nc[1][3], 'ids_hashes': nc[1][4] }),
    
    ops.do_action(lambda o: consesus_succedeed(o['node'], o['branch_index'], o['utxo_history'], o['block_chain'], o['transactions'])),

    # update the global common index
    ops.do_action(lambda o: o['node'].chain.set_max_common_index(
        o['node'].chain.common_index + o['node'].chain.get_global_common_index([c for c in [h['hashes'] for h in o['ids_hashes']]]))),
    ops.do_action(lambda o: print('new max common index: ', o['node'].chain.common_index))
).subscribe()

#
#   CLI PIPELINE
#

rx.combine_latest(
    nodeS,
    commandS
).pipe(
    ops.observe_on(cli_thread_pool),
    ops.do_action(lambda x: execute(x[0], x[1]))
).subscribe()

#
#   COMMUNICATION PIPELINE
#

broadcastS.pipe(
    ops.observe_on(rx.scheduler.NewThreadScheduler()),
    ops.do_action(lambda o: broadcast(o[0],o[1],o[2]))
).subscribe()