import os


if 'env' not in os.environ:
    print('Environment variable not set.')
    os._exit(1)
    
if os.environ['env'] == 'local':
    print('Setting up as local environment')
    bootstrap_ip='127.0.0.1'
    bootstrap_port=25000
    N = 2
    capacity = 5
    difficulty = 4
elif os.environ['env'] == 'remote':
    print('Setting up as remote environment')
    bootstrap_ip='192.168.1.3'
    bootstrap_port=25000
    N = 5
    capacity = 5
    difficulty = 4
else:
    print('Bad environment.')
    os._exit(1)

baseurl_bootstrap = 'http://{}:{}/'.format(bootstrap_ip, bootstrap_port)

transaction_time_stamps = []
block_validation_time_stamps = []
v_transactions = []
pure_transactions = 0
block_mining_time_stamps = []