#!/usr/bin/python3

import requests
import node
import wallet
import sys
import json
import threading
from flask import Flask, jsonify, request, render_template
from Crypto.PublicKey import RSA
from communication import broadcast


def RSA2JSON(rsa):
    return rsa.exportKey("PEM").decode('ascii')

def JSON2RSA(jsonSendable):
    return RSA.importKey(jsonSendable.encode('ascii'))

bootstrap_ip='127.0.0.1'
bootstrap_port=25000
baseurl_bootstrap = 'http://{}:{}/'.format(bootstrap_ip, bootstrap_port)
N = 2

app = Flask(__name__)

@app.route('/get-ring', methods=['POST'])
def update_ring():
    global node
    node.ring = list(request.json.values())[0]
    return jsonify('OK')


def run(ip,port):
    app.run(host=ip, port=port)

def create_node(ip, port):
    node_wallet = wallet.wallet()

    public_key = node_wallet.public_key
    message = {'ip':ip, 'port':port, 'public_key': str(RSA2JSON(public_key))}
    response = requests.post(baseurl_bootstrap + "enter-ring", json = message)

    rejson = response.json()
    myid = rejson["id"]

    return node.node(myid, ip, port, node_wallet)

def bootstrap_node(ip, port):
    node_wallet = wallet.wallet()
    node_boot = node.node(0, ip, port, node_wallet)
    node_boot.ring.append((ip, port, str(RSA2JSON(node_wallet.public_key)),0))
    return node_boot

# bootstrap node
if (len(sys.argv) == 2) and (sys.argv[1] == "boot"):
    print ('Creating bootstrap node')

    node_count = 0
    x = threading.Thread(target=run, args=(bootstrap_ip,bootstrap_port))
    x.start()
    node = bootstrap_node(bootstrap_ip, bootstrap_port)
    
    def register_node_to_ring(node, ip, port, public_key):
		#add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
		#bottstrap node informs all other nodes and gives the request node an id and 100 NBCs
        node.ring.append((ip, port, public_key,0))
        pass

    @app.route('/enter-ring', methods=['POST'])
    def get_data():
        global node_count

        node_count += 1

        ip, port, public_key = list(request.json.values())
        # public_key = JSON2RSA(public_key)
        register_node_to_ring(node, ip, port, public_key)

        response = { 'id': node_count }

        return jsonify(response)


    while node_count != N-1:
        pass

    broadcast([{'ip':host[0],'port':host[1]} for host in node.ring], {'ring':node.ring}, 'get-ring')

    while True:
        pass
    

# non-bootstrap nodes
else:
    if len(sys.argv) != 3:
        print('Bad usage')
        exit(1)

    ip = sys.argv[1]
    port = sys.argv[2]
    x = threading.Thread(target=run, args=(ip,port))
    x.start()

    node = create_node(ip,port)

    while True:
        pass