import rx
from rx import operators as ops
import rx.scheduler

from subscription_utils import do_broadcast_ring, check_correct_running_thread, do_bootstrap_transactions, create_transaction
from blockchain_subjects import nodeS, node_countS, ringS, genesisS, blcS, tsxS, mytsxS, commandS, consensusS
from cli import execute
import settings
from communication import broadcast,lazy_broadcast,unicast

# we define one common thread pool with one available thread to be used by all pipelines
# this way they all run on the same thread => they are serialized and no concurrency control is required
blockchain_thread_pool = rx.scheduler.ThreadPoolScheduler(1)
cli_thread_pool = rx.scheduler.ThreadPoolScheduler(1)

#
#   MAIN PROGRAM PIPELINES
#

# node pipeline - the first to be executed
nodeS.pipe(
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

    # notify genesis is ready and allow transactions to happen
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
    ops.filter(lambda o: o['node'].chain.verify_block(o['bl'])),
    ops.map(lambda o: {'node': o['node'], 'bl': o['bl'], 'utxos': o['node'].validate_block(o['bl'],o['node'].chain.get_recent_UTXOS())}),
    ops.filter(lambda o: o['utxos'] != None),
    ops.do_action(lambda o: o['node'].chain.add_block(o['bl'],o['utxos'])),
    ops.do_action(lambda o: o['node'].clear_current_block()),
    ops.do_action(lambda o: print('Received block: ', o['bl'].stringify()))
).subscribe()

# pipeline for transactions
rx.combine_latest(
    nodeS,
    genesisS,
    tsxS
).pipe(
    ops.observe_on(blockchain_thread_pool),
    ops.do_action(lambda _: check_correct_running_thread()),

    ops.map(lambda nl: {'node': nl[0], 'tx': nl[2], 'utxos': nl[0].get_all_UTXOS()}),

    # verify transaction signature then calculate new utxos. If valid (not None) then update node utxos 
    ops.filter(lambda o: o['tx'].verify_transaction()),

    ops.map(lambda o: {'node': o['node'], 'tx': o['tx'], 'new_utxos': o['node'].validate_transaction(o['tx'], o['utxos'], True)}),
    ops.filter(lambda o: o['new_utxos'] != None),

    ops.do_action(lambda o: o['node'].set_all_utxos(o['new_utxos'])),
    ops.do_action(lambda o: o['node'].add_transaction_to_block(o['tx'])),

    ops.do_action(lambda o: print('Received transaction: ', o['tx'].stringify(o['node']))),
).subscribe()

# pipeline for my transactions
rx.combine_latest(
    nodeS,
    mytsxS
).pipe(
    ops.observe_on(blockchain_thread_pool),
    ops.do_action(lambda _: check_correct_running_thread()),

    ops.map(lambda nl: {'node': nl[0], 'target': nl[1][0], 'amount': nl[1][1]}),
    ops.map(lambda o: {'node': o['node'], 'tx': create_transaction(o['node'],o['target'],o['amount']), 'utxos': o['node'].get_all_UTXOS()}),

    ops.do_action(lambda o: broadcast(o['node'].get_other_hosts(), 'add-transaction', { 'transaction': o['tx'] })),
    
    # verify transaction signature then calculate new utxos. If valid (not None) then update node utxos 
    ops.filter(lambda o: o['tx'].verify_transaction()),

    ops.map(lambda o: {'node': o['node'], 'tx': o['tx'], 'new_utxos': o['node'].validate_transaction(o['tx'], o['utxos'], True)}),
    ops.filter(lambda o: o['new_utxos'] != None),

    ops.do_action(lambda o: o['node'].set_all_utxos(o['new_utxos'])),
    ops.do_action(lambda o: o['node'].add_transaction_to_block(o['tx'])),

    ops.do_action(lambda o: print('Received transaction: ', o['tx'].stringify(o['node']))),
).subscribe()

def consesus_succedeed(node, branch_index, utxo_history, chain, transactions):
    new_chain = node.chain.chain[:branch_index] + chain[-len(utxo_history):]
    new_utxos = node.chain.UTXO_history[:branch_index] +  utxo_history

    my_transactions = []

    for b in node.chain.chain[branch_index:]:
        my_transactions.extend(b.transactions)

    my_transactions.extend(node.current_block)

    transactions_to_add = [t for t in my_transactions if t.transaction_id not in transactions]

    valid_transactions, ring_utxos = node.validate_transactions(transactions_to_add, new_utxos[-1])

    node.current_block = valid_transactions
    node.set_all_utxos(ring_utxos)
    
    node.chain.chain = new_chain
    node.chain.UTXO_history = new_utxos

    print('consesnus reached based on info by node X')


def do_consensus(node, chains):

    index = node.chain.common_index
    print('branch detected at index: ', index)

    for i,chain in chains:
        host = (node.ring[i][0],node.ring[i][1])
        new_index = node.chain.get_max_prefex_chain(chain)
        real_chain = unicast(host, 'request-chain', {'index': new_index})
        utxo_history, branch_index, transactions = node.validate_chain(real_chain, new_index)
        if utxo_history != None:
            consesus_succedeed(node, branch_index, utxo_history, real_chain, transactions)
            return True

    print('Could not achieve consensus')
    return False

rx.combine_latest(
    nodeS,
    consensusS
).pipe(
    ops.observe_on(blockchain_thread_pool),
    ops.do_action(lambda _: check_correct_running_thread()),

    ops.map(lambda nl: {'node': nl[0]}),

    # TODO:
    # hashes = list(map(lambda chain: list(map(lambda block: block.current_hash,chain)),chains))

    ops.map(lambda o: {'node': o['node'], 'chains': broadcast(o['node'].get_other_hosts(), 'request-chain-hash', {'index':o['node'].chain.common_index})}),
    ops.do_action(lambda o: o['node'].chain.set_max_common_index(o['chains'])),
    ops.map(lambda o: {'node': o['node'], 'chains': sorted(list(zip([i for i in range(settings.N) if i != o['node'].id],o['chains'])),reverse = True,key = lambda x: len(x[1]))}),
    ops.do_action(lambda o: do_consensus(o['node'], o['chains'])),
).subscribe()

#
#   CLI PIPELINES
#

rx.combine_latest(
    nodeS,
    commandS
).pipe(
    ops.observe_on(cli_thread_pool),
    ops.do_action(lambda x: execute(x[0], x[1]))
).subscribe()
