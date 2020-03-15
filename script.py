#!/usr/bin/python3

import requests
import node
import wallet
import sys
from flask import Flask, jsonify, request, render_template
from Crypto.PublicKey import RSA


def RSA2JSON(rsa):
    return rsa.exportKey("PEM").decode('ascii')

def JSON2RSA(jsonSendable):
    return RSA.importKey(jsonSendable.encode('ascii'))

bootstrap_ip='127.0.0.1'
bootstrap_port=25000
baseurl_bootstrap = 'http://{}:{}/'.format(bootstrap_ip, bootstrap_port)

app = Flask(__name__)

# bootstrap node
if (len(sys.argv) == 2) and (sys.argv[1] == "boot"):
    print ('Creating bootstrap node')

    node_count = 0

    @app.route('/enter-ring', methods=['POST'])
    def get_data():
        global node_count

        node_count += 1

        public_key = JSON2RSA(list(request.json.values())[0])
        print("got public key %s", str(public_key))

        response = { 'id': node_count }

        return jsonify(response)

    app.run(host=bootstrap_ip, port=bootstrap_port)

# non-bootstrap nodes
else:
    if len(sys.argv) != 3:
        print('Bad usage')
        exit(1)

    ip = sys.argv[1]
    port = sys.argv[2]

    print ('Creating non-bootstrap node')

    node_wallet = wallet.wallet()

    public_key = node_wallet.public_key
    message = { 'public_key': str(RSA2JSON(public_key)) }
    response = requests.post(baseurl_bootstrap + "enter-ring", json = message)

    rejson = response.json()
    myid = rejson["id"]

    print("got id: %d" % myid)

    node = node.node(0, myid, ip, port, node_wallet)

    app.run(host=ip, port=port)