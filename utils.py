from settings import baseurl_bootstrap, bootstrap_ip, bootstrap_port
from Crypto.PublicKey import RSA
import threading
import communication
import wallet
import node
import block
import settings

# create a non-bootstrap node
def create_node(ip, port):
    node_wallet = wallet.wallet()

    public_key = node_wallet.address
    message = { 'ip': ip, 'port': port, 'public_key': public_key }

    response = communication.unicast_bootstrap("enter-ring", message)
    myid = response["id"]

    return node.node(myid, ip, port, node_wallet)

# create a bootstrap node
def create_bootstrap_node():
    node_wallet = wallet.wallet()

    node_boot = node.node(0, bootstrap_ip, bootstrap_port, node_wallet)
    gen_block = block.Block.genesis(node_wallet.address)
    node_boot.chain.chain.append(gen_block)
    genesis_UTXO = {'0':(node_boot.wallet.address,100 * settings.N)}
    node_boot.chain.UTXOS = [genesis_UTXO]+[{} for i in range(settings.N-1)]
    node_boot.ring.append((bootstrap_ip, bootstrap_port, node_wallet.address, genesis_UTXO))

    return node_boot

def startThreadedServer(app, ip, port):
    x = threading.Thread(target=lambda ip, port: app.run(host=ip, port=port), args=(ip, port))
    x.start()
    return x