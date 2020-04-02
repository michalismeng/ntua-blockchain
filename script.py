#!/usr/bin/python3

import requests
import node
import wallet
import block
import sys
import json
from flask import Flask, jsonify, request, render_template, make_response

from settings import bootstrap_ip, bootstrap_port
import utils
import settings
import transaction
from random import uniform
import jsonpickle as jp
import time
import threading
import os
from blockchain_subjects import mytsxS
import cli

# uncomment to disable FLASK messages
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

from blockchain_subjects import nodeS, node_countS, blcS, tsxS, ringS, commandS
import subscriptions        # import to execute them

commands_script = []
command_index = 0

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

@app.route('/request-chain-hash', methods=['POST'])
def request_chain_hash():
    args = jp.decode(request.data)
    n = current_node()
    hashes = n.chain.chain_to_hashes()
    result = { 'hashes': hashes[args['index']:], 'id': n.id }
    print('Hash chain sent')
    return jsonify(result)

@app.route('/request-chain', methods=['POST'])
def request_chain():
    args = jp.decode(request.data)
    n = current_node()
    response = make_response(jp.encode(n.chain.chain[args['index']:]), 200)
    response.mimetype = "text/plain"
    print('Chain sent')
    return response

@app.route('/enter-ring', methods=['POST'])
def get_data():
    create_global_variable('node_count', 1) # initialize to 1 since the bootstrap node is already registered
    global node_count

    if(node_count >= settings.N):
        return jsonify("ERROR")

    args = jp.decode(request.data)
    ip, port, public_key = args['ip'], args['port'], args['public_key']
    utils.register_node_to_ring(current_node(), node, ip, port, public_key)

    response = { 'id': node_count }
    node_countS.on_next(node_count)

    node_count += 1

    return jsonify(response)

@app.route('/load-simulation', methods=['POST'])
def load_senario():
    global commands_script
    command = jp.decode(request.data)['command']
    n = current_node()
    if command.startswith('load'):
        file = command.split()[1]
        with open('transactions/{}nodes/transactions{}.txt'.format(file, n.id), 'r') as f:
            lines = f.readlines()
            commands_script = [ (n.ring[int(x.split(' ')[0][2:])][2],int(x.split(' ')[1]))  for x in lines if int(x.split(' ')[0][2:]) < settings.N ]
            n.commands_script = commands_script
            print('loaded {} commands'.format(len(commands_script)))
            print(commands_script)
            settings.pure_transactions = len(commands_script)
    if command.startswith('run'):
        commandS.on_next('special')
    
    return jsonify('OK')

@app.route('/execute-command', methods=['POST'])
def execute_command():
    global commands_script, command_index
    command = jp.decode(request.data)['command']
    if command.startswith('exec'):
        args = command.split()[1:]
        ids = args[0].split(',')
        if 'id{}'.format(current_node().id) in ids:
            cli.execute(current_node(), ' '.join(args[1:]))

    return jsonify('OK')

@app.route('/management', methods=['POST'])
def management_endpoint():
    global commands_script, command_index
    command = jp.decode(request.data)['command']
    n = current_node()
    if command.startswith('hosts'):
        return jsonify(n.get_hosts())
    elif command.startswith('echo-id'):
        return jsonify((n.id, n.ring[n.id][0], n.ring[n.id][1]))
    elif command.startswith('balance'):
        return jsonify((n.id, [(id, n.get_node_balance(id)) for id in range(settings.N)]))
    elif command.startswith('mining'):
        return jsonify(n.miner.running)
    elif command.startswith('chain'):
        response = make_response(jp.encode((n.id,n.chain.get_block_indexes()),keys=True), 200)
        response.mimetype = "text/plain"
        return response
    return jsonify('OK')

@app.route('/get-stats', methods=['POST'])
def get_stat():
    n = current_node()
    stats = {'id': n.id,
            'tsx': settings.transaction_time_stamps,
            'blc': settings.block_validation_time_stamps,
            'vtsx': settings.v_transactions,
            'ptsx': settings.pure_transactions,
            'mblc': settings.block_mining_time_stamps}
    response = make_response(jp.encode(stats), 200)
    response.mimetype = "text/plain"
    return response

# bootstrap node
if (len(sys.argv) == 2) and (sys.argv[1] == "boot"):

    # settings.difficulty = 4

    def current_node(): 
        global bootstrap_node
        return bootstrap_node

    print('Creating bootstrap node')

    bootstrap_node = utils.create_bootstrap_node()
    nodeS.on_next(bootstrap_node)
    utils.startThreadedServer(app, bootstrap_ip, bootstrap_port)

# non-bootstrap nodes
else:
    if len(sys.argv) != 3:
        print('Bad usage')
        exit(1)

    ip = sys.argv[1]
    port = int(sys.argv[2])

    def current_node(): 
        global miner_node
        return miner_node

    miner_node = utils.create_node(ip, port)
    nodeS.on_next(miner_node)
    utils.startThreadedServer(app, ip, port)
