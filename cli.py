from subscription_utils import do_block, create_transaction
from blockchain_subjects import mytsxS, blcS
import block
import os
import time
import random
from communication import unicast
from miner import Miner


def execute(n, s):
    if s == 'special':
        random.seed(9001 * n.id)
        for com in n.commands_script:
            time.sleep(random.uniform(0,3))
            mytsxS.on_next(com)
    elif s == 'exit':
        os._exit(0)
    elif s == 'utxos':
        print(n.get_node_UTXOS(n.id))
    elif str.startswith(s, 'balance'):
        values = s.split(' ')
        if len(values) == 1:        # if no argument is supplied, assume current node balance is requested
            values.append(n.id)
        for id in values[1:]:
            print('Balance of node {}: {}'.format(id, n.get_node_balance(int(id))))
    elif s == 'all_utxos':
        print(n.get_all_UTXOS())
    elif s == 'chain':
        print([c.current_hash for c in n.chain.chain])
        print(n.chain.get_block_indexes())
        # print(n.chain.UTXO_history)
    elif s == 'block':
        print(n.get_pending_transactions())

    elif s == 'ci':
        print(n.chain.common_index)
    
    elif s == 'mine':
        print(n.look_for_ore_block().current_hash)

    elif s.startswith('tu'):
        _, id, amount = s.split(' ')
        t = create_transaction(n, n.ring[int(id)][2], int(amount))
        host = (n.ring[int(id)][0], n.ring[int(id)][1])
        unicast(host, 'add-transaction', { 'transaction': t})

    elif s.startswith('th'):
        _, id, amount = s.split(' ')
        t = create_transaction(n, n.ring[int(id)][2], int(amount))
        new_utxos = n.validate_transaction(t, n.get_all_UTXOS(), True)
        if new_utxos == None:
            print('ERROR')
        n.set_all_utxos(new_utxos)
        n.add_transaction_to_block(t)

    elif s.startswith('t'):
        _, id, amount = s.split(' ')
        mytsxS.on_next((n.ring[int(id)][2], int(amount)))

    elif s.startswith('b'):
        _, id = s.split(' ')

        m = Miner()
        b = n.look_for_ore_block()
        m.mine(b, n.id)

        print('found valid block')
        host = (n.ring[int(id)][0], n.ring[int(id)][1])
        unicast(host, 'add-block', { 'block': b })

    elif s.startswith('s'):
        
        m = Miner()
        b = n.look_for_ore_block()
        m.mine(b, n.id)

        print('found valid block')
        blcS.on_next(b)
        do_block(n, b)