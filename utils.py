from settings import baseurl_bootstrap, bootstrap_ip, bootstrap_port
from Crypto.PublicKey import RSA
import threading
import communication
import wallet
import node

# convert RSA object to JSON
def RSA2JSON(rsa):
    return rsa.exportKey("PEM").decode('ascii')

# convert json to RSA
def JSON2RSA(jsonSendable):
    return RSA.importKey(jsonSendable.encode('ascii'))

# create a non-bootstrap node
def create_node(ip, port):
    node_wallet = wallet.wallet()

    public_key = node_wallet.public_key
    message = { 'ip': ip, 'port': port, 'public_key': RSA2JSON(public_key) }

    response = communication.unicast_bootstrap("enter-ring", message)
    myid = response["id"]

    return node.node(myid, ip, port, node_wallet)

# create a bootstrap node
def create_bootstrap_node():
    node_wallet = wallet.wallet()

    node_boot = node.node(0, bootstrap_ip, bootstrap_port, node_wallet)
    node_boot.ring.append((bootstrap_ip, bootstrap_port, node_wallet.public_key, 0))

    return node_boot

def startThreadedServer(app, ip, port):
    x = threading.Thread(target=lambda ip, port: app.run(host=ip, port=port), args=(ip, port))
    x.start()
    return x