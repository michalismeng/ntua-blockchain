#!/usr/bin/python3

import requests
import node
import wallet
import sys
import json
from flask import Flask, jsonify, request, render_template

from communication import broadcast
from settings import bootstrap_ip, bootstrap_port
import utils
import settings
import time
import transaction
import rx
from rx import operators as ops
from rx.subject import Subject, ReplaySubject
import jsonpickle as jp

# uncomment to disable FLASK messages
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# transaction subject
tsxS = ReplaySubject()

# ring subject
ringS = ReplaySubject()

# node subject
nodeS = ReplaySubject()

nodeO = nodeS.pipe(
    ops.do_action(lambda miner: print("Created miner with id: ", miner.id))
)

rx.zip(
    nodeO, 
    ringS,
).pipe(
    ops.do_action(lambda c: print('Received ring'))
).subscribe(lambda x: x[0].set_ring(x[1]))

rx.combine_latest(
    nodeS,
    tsxS
).pipe(
    ops.map(lambda nl: { 'node': nl[0], 'tx': nl[1] }),
).subscribe(lambda o: o['node'].current_block.append(o['tx']))

app = Flask(__name__)
def create_global_variable(name, value):
    if name not in globals():
        globals()[name] = value

@app.route('/get-ring', methods=['POST'])
def update_ring():
    args = jp.decode(request.data)
    ringS.on_next(args['ring'])
    print('broadcast success')
    return jsonify('OK')

@app.route('/add-transaction', methods=['POST'])
def add_transaction():
    args = jp.decode(request.data)
    t = args['transaction']
    tsxS.on_next(t)
    if t.verify_transaction():
        pass
        # current_node().chain.add_transaction(t)     # TODO: Validate
        # tsxS.on_next(t)

    return jsonify('OK')

def register_node_to_ring(node, ip, port, public_key):
    # add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
    # bottstrap node informs all other nodes and gives the request node an id and 100 NBCs
    print('adding node {}:{} to ring'.format(ip, port))
    bootstrap_node.ring.append((ip, port, public_key, 0))

def do_broadcast_ring():
    print('broadcating ring to all nodes...')
    print('hosts ', bootstrap_node.ring)
    broadcast(bootstrap_node.get_hosts(), 'get-ring', { 'ring': bootstrap_node.ring })

    for _, _, public_key, _ in bootstrap_node.ring[1:]:     # exclude self
        t = transaction.Transaction(bootstrap_node.wallet.address, public_key, 100, bootstrap_node.NBC)
        t.sign_transaction(bootstrap_node.wallet.private_key)
        broadcast(bootstrap_node.get_hosts(),'add-transaction', { 'transaction': t })

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
        pass


# non-bootstrap nodes
else:
    if len(sys.argv) != 3:
        print('Bad usage')
        exit(1)

    ip = sys.argv[1]
    port = sys.argv[2]

    def current_node(): 
        global miner_node
        return miner_node

    utils.startThreadedServer(app, ip, port)
    miner_node = utils.create_node(ip, port)
    nodeS.on_next(miner_node)

    while True:
        x = input()
        print(jp.encode(current_node().current_block))
