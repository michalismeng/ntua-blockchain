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
from rx.subject import Subject
import jsonpickle as jp

app = Flask(__name__)
def create_global_variable(name, value):
    if name not in globals():
        globals()[name] = value

@app.route('/get-ring', methods=['POST'])
def update_ring():
    args = jp.decode(request.data)
    current_node().ring = args['ring']
    print('broadcast success')
    return jsonify('OK')

@app.route('/add-transaction', methods=['POST'])
def add_transaction():
    args = jp.decode(request.data)
    t = args['transaction']
    if t.verify_transaction():
        current_node().chain.add_transaction(t)     # TODO: Validate
        ledger.on_next(current_node().chain)

    return jsonify('OK')

ledger = Subject()

def register_node_to_ring(node, ip, port, public_key):
    # add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
    # bottstrap node informs all other nodes and gives the request node an id and 100 NBCs
    print('adding node {}:{} to ring'.format(ip, port))
    bootstrap_node.ring.append((ip, port, public_key, 0))
    
    t = transaction.Transaction(bootstrap_node.wallet.address, public_key, 100, bootstrap_node.NBC)

    t.sign_transaction(bootstrap_node.wallet.private_key)
    broadcast(bootstrap_node.get_hosts(),'add-transaction',{'transaction': t})

def do_broadcast_ring():
    print('broadcating ring to all nodes...')
    broadcast([(ip, port) for ip, port, _, _ in bootstrap_node.ring], 'get-ring', { 'ring': bootstrap_node.ring })

# bootstrap node
if (len(sys.argv) == 2) and (sys.argv[1] == "boot"):

    def current_node(): 
        global bootstrap_node
        return bootstrap_node

    print('Creating bootstrap node')

    utils.startThreadedServer(app, bootstrap_ip, bootstrap_port)
    bootstrap_node = utils.create_bootstrap_node()

    source = Subject()

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
        node_count += 1
        source.on_next(node_count)

        return jsonify(response)

    source.pipe(
        ops.filter(lambda n: n == settings.N)
    ).subscribe(lambda x: do_broadcast_ring())

    ledger.subscribe(lambda chain: print('Updated chain: ', jp.encode(chain)))
    
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

    print('created node with id: ', miner_node.id)

    ledger.subscribe(lambda chain: print('Updated chain: ', jp.encode(chain)))

    while True:
        pass
