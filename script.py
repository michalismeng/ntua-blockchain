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

import rx
from rx import operators as ops
from rx.subject import Subject

app = Flask(__name__)


@app.route('/get-ring', methods=['POST'])
def update_ring():
    args = request.get_json()
    current_node.ring = list(request.json.values())[0]
    print('broadcast success')
    print('current ring', current_node.ring)
    return jsonify('OK')


def register_node_to_ring(node, ip, port, public_key):
    # add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
    # bottstrap node informs all other nodes and gives the request node an id and 100 NBCs
    print('adding node {}:{} to ring'.format(ip, port))
    bootstrap_node.ring.append((ip, port, public_key, 0))
    pass

def do_broadcast_ring():
    print('broadcating ring to all nodes...')
    message = list(map(lambda r: (r[0], r[1], utils.RSA2JSON(r[2]), r[3]), bootstrap_node.ring))
    broadcast([(ip, port) for ip, port, _, _ in bootstrap_node.ring], 'get-ring', {'ring': message})

# bootstrap node
if (len(sys.argv) == 2) and (sys.argv[1] == "boot"):

    def current_node(): return bootstrap_node

    print('Creating bootstrap node')

    utils.startThreadedServer(app, bootstrap_ip, bootstrap_port)
    bootstrap_node = utils.create_bootstrap_node()
    node_count = 1

    source = Subject()

    @app.route('/enter-ring', methods=['POST'])
    def get_data():
        global node_count

        if(node_count >= settings.N):
            return jsonify("ERROR")

        args = request.get_json()
        ip, port, public_key = args['ip'], args['port'], args['public_key']
        register_node_to_ring(node, ip, port, utils.JSON2RSA(public_key))

        response = {'id': node_count}
        node_count += 1
        source.on_next(node_count)

        return jsonify(response)

    source.pipe(
        ops.filter(lambda n: n == settings.N)
    ).subscribe(lambda x: do_broadcast_ring())
    
    while True:
        pass


# non-bootstrap nodes
else:
    if len(sys.argv) != 3:
        print('Bad usage')
        exit(1)

    def current_node(): return node

    ip = sys.argv[1]
    port = sys.argv[2]

    utils.startThreadedServer(app, ip, port)
    node = utils.create_node(ip, port)

    print('created node with id: ', node.id)

    while True:
        pass
