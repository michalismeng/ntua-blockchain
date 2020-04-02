#!/usr/bin/env python3

import requests
import communication
import settings
import cmd, sys
import time
from functools import reduce

def geomean(array):
    filtered = [x for x in array if x != 'NaN']
    return reduce(lambda x, y: x * y, filtered) ** (1/len(filtered))

class RouterShell(cmd.Cmd):
    def __init__(self, hosts):
        super().__init__()
        self.hosts = hosts

    intro = 'Welcome to noobcoin\n'
    prompt = '(client) '

    # Old and dirty API
    def do_exec(self, args):
        communication.broadcast(hosts, 'execute-command', { 'command': 'exec ' + args })

    # Management
    def do_ping(self, args):
        nodes = communication.broadcast(hosts, 'management', { 'command': 'echo-id' })
        for id, ip, port in nodes:
            print('Node {} is alive at {}:{}'.format(id, ip, port))

        if len(nodes) == len(hosts):
            print('All nodes are alive')
        else:
            print('Warning! Some nodes did not respond')

    def do_balance(self, args):
        id_balance = communication.broadcast(hosts, 'management', { 'command': 'balance' })
        for node_id, balances in id_balance:
            print('Node {} has balances: ({})'.format(node_id, ' '.join([str((id, balance)) for id, balance in balances])))

    def do_chain(self, args):
        chains = communication.broadcast(hosts, 'management', { 'command': 'chain' })
        for id, chain in chains:
            print('Node {} has chain indices:'.format(id))
            print(chain)

    def do_mine(self, args):
        print('Nodes that are mining')
        print(communication.broadcast(hosts, 'management', { 'command': 'mining' }))

    # Load and start simulation
    def do_sst(self, args):
        communication.broadcast(hosts, 'load-simulation', { 'command': 'load ' + args })
        communication.broadcast(hosts, 'load-simulation', { 'command': 'run'})
    
    # Get stats
    def do_stats(self, args):
        stats = communication.broadcast(hosts, 'get-stats', { })
        min_time = stats[0]['tsx'][settings.N-1][0]
        max_time = stats[0]['blc'][-1][0]
        trx = 0
        res2 = []
        for stat in stats:
            print('Node', stat['id'])
            print('Total transactions received: ', len(stat['tsx'][settings.N-1:]))
            print('Total valid transactions: ', len(stat['vtsx'][settings.N-1:]))
            print('Total transactions issued: ', stat['ptsx'])

            if len(stat['mblc']) == 0:
                res2.append('NaN')
            else:
                res2.append(sum([x for x,_,_ in stat['mblc']]) / len(stat['mblc']))            

            trx += stat['ptsx']
            if stat['tsx'][settings.N-1][0] < min_time:
                min_time = stat['tsx'][settings.N-1][0]
            if stat['blc'][-1][0] >  max_time:
                max_time = stat['blc'][-1][0]
        
        res = trx / (max_time - min_time)

        print('Transaction throughput: {}'.format(res))
        print('Block time for each node: {}'.format(res2))

    
if __name__ == '__main__':
    hosts = communication.unicast_bootstrap('management', { 'command': 'hosts' })
    RouterShell(hosts).cmdloop()