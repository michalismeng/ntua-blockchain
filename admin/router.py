#!/usr/bin/env python3

import requests
import cmd, sys
import time
from functools import reduce
import argparse
import jsonpickle as jp
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('boot_host', metavar='bootstrap host', type=str, help='Bootstrap ip:port pair')

def broadcast(hosts, api, message):
    responses = []
    message = jp.encode(message, keys=True)

    for ip, port in hosts:
        try:
            response = requests.post('http://{}:{}/{}'.format(ip, port, api), message)
            responses.append(jp.decode(response.text, keys = True))

        except:
            pass
    
    return responses

def geomean(array):
    filtered = [x for x in array if x != 'NaN']
    return reduce(lambda x, y: x * y, filtered) ** (1/len(filtered))

class RouterShell(cmd.Cmd):
    def __init__(self, bootstrap_host):
        super().__init__()
        self.bootstrap_host = bootstrap_host
        self.hosts = []
        self.N, self.capacity, self.difficulty = None, None, None
        if(len(broadcast([self.bootstrap_host], 'management', { 'command': 'echo-id' })) == 1):
            self.do_hosts(None)
            self.do_configuration(None)

    intro = 'Welcome to noobcoin\n'
    prompt = '(client) '

    def do_setall(self, args):
        subprocess.call(["./exec_on_all.sh run_node.sh {}".format(args)],shell=True)
    
    def do_killall(self, args):
        subprocess.check_call("./exec_on_all.sh kill_all.sh",   shell=True)

    # Old and dirty API
    def do_exec(self, args):
        broadcast(self.hosts, 'execute-command', { 'command': 'exec ' + args })

    # Management
    def do_hosts(self, args):
        # use broadcast to unicast
        self.hosts = broadcast([self.bootstrap_host] ,'management', { 'command': 'hosts' })[0]
        print('Found hosts: ')
        print(self.hosts)

    def do_configuration(self, args):
        # use broadcast to unicast
        self.N, self.capacity, self.difficulty = broadcast([self.bootstrap_host] ,'management', { 'command': 'config' })[0]
        print('Current configuration: ')
        print('N: {}, Capacity: {}, Difficulty: {}'.format(self.N, self.capacity, self.difficulty))
        
    def do_ping(self, args):
        nodes = broadcast(self.hosts, 'management', { 'command': 'echo-id' })
        for id, ip, port in nodes:
            print('Node {} is alive at {}:{}'.format(id, ip, port))

        if len(nodes) == len(self.N):
            print('All nodes are alive')
        else:
            print('Warning! Some nodes did not respond')

    def do_balance(self, args):
        id_balance = broadcast(self.hosts, 'management', { 'command': 'balance' })
        for node_id, balances in id_balance:
            print('Node {} has balances: ({})'.format(node_id, ' '.join([str((id, balance)) for id, balance in balances])))

    def do_chain(self, args):
        chains = broadcast(self.hosts, 'management', { 'command': 'chain' })
        for id, chain in chains:
            print('Node {} has chain indices:'.format(id))
            print(chain)

    def do_view(self, args):
        lastTransactionsIDs = broadcast(self.hosts, 'management', { 'command': 'view' })

        for id, lastTransactions in lastTransactionsIDs:
            print('Node {} last transactions: '.format(id))
            for sender, receiver, amount in lastTransactions:
                print('  Transaction from id{} to id{} with amount {}'.format(sender, receiver, amount))


    def do_mine(self, args):
        print('Nodes that are mining')
        print(broadcast(self.hosts, 'management', { 'command': 'mining' }))

    # Execution
    def do_t(self, args):
        if len(args.split(' ')) != 3:
            print('Usage: t idSrc idDst amount')
            return
        
        idSrc, idDst, amount = args.split(' ')
        broadcast(self.hosts, 'execute-command', { 'command': 'exec {} t {} {}'.format(idSrc, idDst[2:], amount) })

    # Load and start simulation
    def do_sst(self, args):
        broadcast(self.hosts, 'load-simulation', { 'command': 'load ' + args })
        broadcast(self.hosts, 'load-simulation', { 'command': 'run'})
    
    # Get stats
    def do_stats(self, args):
        stats = broadcast(self.hosts, 'get-stats', { })
        min_time = stats[0]['tsx'][self.N-1][0]
        max_time = stats[0]['blc'][-1][0]
        trx = 0
        res2 = []
        res22 = []
        for stat in stats:
            print('Node', stat['id'])
            print('Total transactions received: ', len(stat['tsx']))
            print('Total valid transactions: ', len(stat['vtsx']))
            print('Total transactions issued: ', stat['ptsx'])

            if len(stat['mblc']) == 0:
                res2.append('NaN')
            else:
                res2.append(sum([x for x,_,_ in stat['mblc']]) / len(stat['mblc']))         
                res22.append(geomean([x for x,_,_ in stat['mblc']]))   

            trx += stat['ptsx']
            if stat['tsx'][self.N-1][0] < min_time:
                min_time = stat['tsx'][self.N-1][0]
            if stat['blc'][-1][0] >  max_time:
                max_time = stat['blc'][-1][0]
        
        res = trx / (max_time - min_time)

        print('Transaction throughput: {}'.format(res))
        print('Block time for each node: {}'.format(res2))
        print('Geomean Block time for each node: {}'.format(res22))
        print('Mean of block time: {}'.format(geomean(res2)))
        print('Geomean of block time: {}'.format(geomean(res22)))

    
if __name__ == '__main__':
    args = parser.parse_args()

    # check that boot ip is OK
    if ':' not in args.boot_host:
        print('Could not parse ip, port pair')
        exit(1)
    
    # get ip, port of bootstrap node
    ip, port = args.boot_host.split(':')

    RouterShell((ip, port)).cmdloop()