from subscription_utils import do_transaction, do_block
import block
import os

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
    elif s == 'block':
        print(n.get_pending_transactions())
    elif str.startswith(s, 't'):
        _, id, amount = s.split(' ')
        do_transaction(n, n.ring[int(id)][2], int(amount))
    elif s == 's':
        b = block.Block(1, 0, 0)
        b.transactions = n.current_block
        do_block(n, b)