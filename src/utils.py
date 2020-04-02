from settings import baseurl_bootstrap, bootstrap_ip, bootstrap_port
from Crypto.PublicKey import RSA
import threading
import communication
import wallet
import node
import block
import settings
import random

# should be called by the bootstrap node
def register_node_to_ring(bootstrap_node, node, ip, port, public_key):
    print('adding node {}:{} to ring'.format(ip, port))
    bootstrap_node.ring.append((ip, port, public_key, {}))

# create a non-bootstrap node
def create_node(ip, port):
    node_wallet = wallet.wallet()

    public_key = node_wallet.address
    message = { 'ip': ip, 'port': port, 'public_key': public_key }

    response = communication.unicast_bootstrap("enter-ring", message)
    myid = response["id"]
    # random.seed(9001 * int(myid))
    return node.node(myid, ip, port, node_wallet)

def create_bootstrap_node():
    node_wallet = wallet.wallet()

    node_boot = node.node(0, bootstrap_ip, bootstrap_port, node_wallet)
    register_node_to_ring(node_boot, node_boot, bootstrap_ip, bootstrap_port, node_wallet.address)
    # random.seed(9001 * int(0))
    return node_boot

def startThreadedServer(app, ip, port):
    # x = threading.Thread(target=lambda ip, port: app.run(host=ip, port=port), args=(ip, port))
    # x.start()

    app.run(host=ip, port=port)
    return

def get_max_common_prefix_length(list1, list2):
    # l = [item1 != item2 for item1, item2 in zip(list1, list2)] + [1]
    # l.index(min(l))
    for i, (item1, item2) in enumerate(zip(list1, list2)):
        if(item1 != item2):
            return i
    return min(len(list1), len(list2))