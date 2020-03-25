from subscription_utils import do_transaction, do_block
from blockchain_subjects import mytsxS
import block
import os
from communication import unicast

def execute(n, s):
    if s == 'exit':
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
        print(n.chain.get_block_indexes())
        print(n.chain.get_recent_UTXOS())
    elif s == 'block':
        print(n.get_pending_transactions())
    elif str.startswith(s, 't'):
        _, id, amount = s.split(' ')
        mytsxS.on_next((n.ring[int(id)][2], int(amount)))
    elif s.startswith('b'):
        index = n.chain.get_last_block().index+1
        hs = n.chain.get_last_block().current_hash
        b = block.Block(index, hs, 0)
        host = (n.ring[1][0], n.ring[1][1])
        unicast(host, 'add-block', { 'block': b })
    elif s.startswith('s'):
        values = s.split(' ')
        if len(values) == 1:
            values.append(n.chain.get_last_block().index+1)
        if len(values) == 2:
            values.append(n.chain.get_last_block().current_hash)
        _, index, hs = values
        b = block.Block(index, hs, 0)
        b.transactions = n.current_block
        do_block(n, b)