import rx
from rx import operators as ops
import rx.scheduler

from subscription_utils import do_broadcast_ring, check_correct_running_thread, do_bootstrap_transactions, do_validate_transaction
from blockchain_subjects import nodeS, node_countS, ringS, genesisS, blcS, tsxS, commandS
from cli import execute
import settings

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
    ops.observe_on(rx.scheduler.ThreadPoolScheduler(1)),
    ops.map(lambda nc: { 'boot_node': nc[0], 'count': nc[1] }),

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

    ops.map(lambda nb: { 'node': nb[0], 'bl': nb[1] }),
    ops.filter(lambda o: o['bl'].previous_hash == 1),               # check if this is a genesis block
    ops.filter(lambda o: o['node'].chain.in_genesis_state()),       # check that this is the first (and only) genesis block to arrive
    ops.map(lambda o: { 'node': o['node'], 'bl': o['bl'], 'tsx': o['bl'].transactions[0] }),

    # add genesis block to blockchain and configure utxos
    ops.do_action(lambda o: o['node'].chain.add_block(o['bl'])),
    ops.do_action(lambda o: o['node'].chain.set_utxos([{o['tsx'].transaction_id: (o['node'].ring[0][2], 100 * settings.N)}] + [{} for i in range(settings.N-1)])),
    ops.do_action(lambda o: o['node'].set_all_utxos(o['node'].chain.UTXOS)),

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

    ops.map(lambda nl: { 'node': nl[0], 'bl': nl[1] }),

    ops.filter(lambda o: o['bl'].previous_hash != 1),           # check that this is not a genesis block

    # # ops.filter(lambda o: o['bl'].verify_block()),
    ops.filter(lambda o: o['node'].validate_block(o['bl'])),
    ops.do_action(lambda o: o['node'].chain.add_block(o['bl'])),
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

    ops.map(lambda nl: { 'node': nl[0], 'tx': nl[2] }),

    ops.filter(lambda o: o['tx'].verify_transaction()),
    ops.filter(lambda o: do_validate_transaction(o['node'], o['tx'])),

    ops.do_action(lambda o: print('Received transaction: ', o['tx'].stringify(o['node']))),
    ops.do_action(lambda o: o['node'].add_transaction_to_block(o['tx'])),
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