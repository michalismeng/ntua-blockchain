#!/usr/bin/python3

import requests
import node
import wallet
import sys
import json
from flask import Flask, jsonify, request, render_template

from communication import broadcast, unicast
from settings import bootstrap_ip, bootstrap_port
import utils
import settings
import transaction
import rx
from rx import operators as ops
from rx.subject import Subject, ReplaySubject
import rx.scheduler
import jsonpickle as jp
import time
import threading
import os

# uncomment to disable FLASK messages
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# thread_pool = rx.scheduler.ThreadPoolScheduler(5)
# new_thread = NewThreadScheduler()

# transaction subject
tsxS = Subject()

# block subject
blcS = Subject()

# ring subject
ringS = Subject()

# node subject
nodeS = Subject()

# command subject
commandS = Subject()

nodeS.subscribe(lambda miner: print("Created miner with id: ", miner.id))

rx.combine_latest(
    nodeS,
    blcS
).pipe(
    ops.observe_on(rx.scheduler.ThreadPoolScheduler(1)),
    # ops.do_action(lambda x: print(threading.currentThread().name)),
    
    ops.map(lambda nl: { 'node': nl[0], 'bl': nl[1] }),
    # ops.filter(lambda o: o['bl'].verify_block()),
    ops.filter(lambda o: o['node'].validate_block(o['bl'])),
    ops.do_action(lambda o: o['node'].add_block_to_chain(o['bl'])),
    ops.do_action(lambda o: o['node'].clear_current_block()),
    ops.do_action(lambda o: print('Received block: ', o['bl'].stringify()))
).subscribe()

rx.zip(
    nodeS, 
    ringS,
).pipe(
    ops.do_action(lambda x: x[0].set_ring(x[1])),
    ops.do_action(lambda x: print('Current ring: ', x[0].get_hosts())),
).subscribe()

# def broadcast_needed(n,t):
#     b = n.add_transaction_to_block(t)
#     if b != None:
#         do_block(n,block = b)

def do_validdate_transaction(n,t):
    temp_UTXOS = n.validate_transaction(t, n.get_all_UTXOS())
    if temp_UTXOS == None:
        return False
    n.set_all_utxos(temp_UTXOS)
    return True

rx.combine_latest(
    nodeS,
    tsxS
).pipe(
    ops.observe_on(rx.scheduler.ThreadPoolScheduler(1)),
    # ops.do_action(lambda x: print(threading.currentThread().name)),
    ops.map(lambda nl: { 'node': nl[0], 'tx': nl[1] }),
    ops.filter(lambda o: o['tx'].verify_transaction()),
    ops.filter(lambda o: do_validdate_transaction(o['node'],o['tx'])),
    ops.do_action(lambda o: print('Received transaction: ', o['tx'].stringify(o['node']))),
    ops.do_action(lambda o: o['node'].add_transaction_to_block(o['tx']))
).subscribe()

def execute(n,s):
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
        import block
        b = block.Block(1, 0, 0)
        b.transactions = n.current_block
        do_block(n, block=b)

rx.combine_latest(
    nodeS,
    commandS
).pipe(
    ops.observe_on(rx.scheduler.ThreadPoolScheduler(1))
).subscribe(
    lambda x: execute(x[0],x[1])
)

app = Flask(__name__)
def create_global_variable(name, value):
    if name not in globals():
        globals()[name] = value

@app.route('/get-ring', methods=['POST'])
def update_ring():
    args = jp.decode(request.data)
    ringS.on_next(args['ring'])
    return jsonify('OK')

@app.route('/add-transaction', methods=['POST'])
def add_transaction():
    args = jp.decode(request.data)
    tsxS.on_next(args['transaction'])
    return jsonify('OK')

@app.route('/add-block', methods=['POST'])
def add_block():
    args = jp.decode(request.data)
    blcS.on_next(args['block'])
    return jsonify('OK')

def register_node_to_ring(node, ip, port, public_key):
    # add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
    # bottstrap node informs all other nodes and gives the request node an id and 100 NBCs
    print('adding node {}:{} to ring'.format(ip, port))
    bootstrap_node.ring.append((ip, port, public_key, {}))

def do_transaction(sender_node, target_key, amount):
    UTXO_ids, UTXO_sum = sender_node.get_suffisient_UTXOS(amount)
    t = transaction.Transaction(sender_node.wallet.address, target_key, amount, UTXO_sum, UTXO_ids)
    t.sign_transaction(sender_node.wallet.private_key)
    broadcast(sender_node.get_hosts(), 'add-transaction', { 'transaction': t })

def do_block(sender_node, address = None,block = None):
    if block == None:
        unicast(sender_node.address_to_host(address), 'add-block', { 'block': sender_node.chain.get_last_block()})
    else:
        broadcast(sender_node.get_hosts(), 'add-block', { 'block': block })

def do_broadcast_ring():
    print('broadcating ring to all nodes...')
    broadcast(bootstrap_node.get_hosts(), 'get-ring', { 'ring': bootstrap_node.ring })

    for _, _, public_key, _ in bootstrap_node.ring[1:]:     # exclude self
        do_block(bootstrap_node, public_key)
        do_transaction(bootstrap_node, public_key, 100)


# bootstrap node
if (len(sys.argv) == 2) and (sys.argv[1] == "boot"):

    def current_node(): 
        global bootstrap_node
        return bootstrap_node

    print('Creating bootstrap node')

    utils.startThreadedServer(app, bootstrap_ip, bootstrap_port)
    bootstrap_node = utils.create_bootstrap_node()
    nodeS.on_next(bootstrap_node)

    # node count subject
    node_countS = ReplaySubject()

    node_countS.pipe(
        ops.observe_on(rx.scheduler.ThreadPoolScheduler(2)),       # force usage of another thread, othrwise broadcast fails
        ops.filter(lambda n: n == settings.N - 1),
    ).subscribe(lambda x: do_broadcast_ring())

    @app.route('/enter-ring', methods=['POST'])
    def get_data():
        create_global_variable('node_count', 1) # initialize to 1 since the bootstrap node is already registered
        global node_count

        if(node_count >= settings.N):
            return jsonify("ERROR")

        args = jp.decode(request.data)
        ip, port, public_key = args['ip'], args['port'], args['public_key']
        register_node_to_ring(node, ip, port, public_key)

        response = { 'id': node_count }
        node_countS.on_next(node_count)

        node_count += 1

        return jsonify(response)

    while True:
        x = input()
        commandS.on_next(x)


# non-bootstrap nodes
else:
    if len(sys.argv) != 3:
        print('Bad usage')
        exit(1)

    ip = sys.argv[1]
    port = int(sys.argv[2])

    # time.sleep(2)

    def current_node(): 
        global miner_node
        return miner_node

    utils.startThreadedServer(app, ip, port)
    miner_node = utils.create_node(ip, port)
    nodeS.on_next(miner_node)

    while True:
        x = input()
        commandS.on_next(x)
        
