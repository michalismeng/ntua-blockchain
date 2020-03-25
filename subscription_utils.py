import threading

import os
import block
import transaction
from communication import broadcast

import time

# debug function to ensure all subscriptions run on the same thread
def check_correct_running_thread():
    if threading.currentThread().name != "ThreadPoolExecutor-0_0":
        print('Subscription runs on wrong thread')
        print('terminating...')
        os._exit(0)

# execute first N - 1 transactions to all node except the bootstrap node
def do_bootstrap_transactions(bootstrap_node):
    for _, _, public_key, _ in bootstrap_node.ring[1:]:     # exclude self
        do_transaction(bootstrap_node, public_key, 100)

def do_transaction(sender_node, target_key, amount):
    print(sender_node.get_suffisient_UTXOS(amount))
    UTXO_ids, UTXO_sum = sender_node.get_suffisient_UTXOS(amount)
    t = transaction.Transaction(sender_node.wallet.address, target_key, amount, UTXO_sum, UTXO_ids)
    t.sign_transaction(sender_node.wallet.private_key)
    broadcast(sender_node.get_hosts(), 'add-transaction', { 'transaction': t })

def do_genesis_block(bootstrap_node):
    gen_block = block.Block.genesis(bootstrap_node.wallet.address)
    broadcast(bootstrap_node.get_hosts(), 'add-block', { 'block': gen_block })

def do_block(sender_node, block):
    broadcast(sender_node.get_hosts(), 'add-block', { 'block': block })

def do_broadcast_ring(bootstrap_node):
    print('broadcating ring to all nodes...')
    broadcast(bootstrap_node.get_hosts(), 'get-ring', { 'ring': bootstrap_node.ring })
    do_genesis_block(bootstrap_node)