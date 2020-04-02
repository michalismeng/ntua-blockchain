import os


if 'env' not in os.environ:
    print('Environment variable not set.')
    os._exit(1)
    
if os.environ['env'].startswith('local'):
    bootstrap_ip='127.0.0.1'
    bootstrap_port=25000
    if '-' in os.environ['env']:
        N, capacity, difficulty = [int(x) for x in os.environ['env'].split('-')[1:]]
    else:
        N = 2
        capacity = 5
        difficulty = 3
    print('Setting up as local environment with N={}, capacity={}, difficulty={}'.format(N, capacity, difficulty))
elif os.environ['env'].startswith('remote'):
    if '-' not in os.environ['env']:
        print('Remote environment must be remote-[N]-[capacity]-[difficulty]')
        os._exit(1)
    bootstrap_ip='192.168.1.3'
    bootstrap_port=25000
    N, capacity, difficulty = [int(x) for x in os.environ['env'].split('-')[1:]]
    print('Setting up as remote environment with N={}, capacity={}, difficulty={}'.format(N, capacity, difficulty))
else:
    print('Bad environment.')
    os._exit(1)

baseurl_bootstrap = 'http://{}:{}/'.format(bootstrap_ip, bootstrap_port)

transaction_time_stamps = []
block_validation_time_stamps = []
v_transactions = []
pure_transactions = 0
block_mining_time_stamps = []