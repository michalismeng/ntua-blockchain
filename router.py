#!/usr/bin/env python3

import requests
import communication
import settings
import cmd, sys
import time

class RouterShell(cmd.Cmd):
    def __init__(self, hosts):
        super().__init__()
        self.hosts = hosts

    intro = 'Welcome to noobcoin\n'
    prompt = '(client) '

    def do_exec(self, args):
        communication.broadcast(hosts, 'execute-command', { 'command': 'exec ' + args })

    def do_ping_all(self, args):
        ids = communication.broadcast(hosts, 'management', { 'command': 'echo-id' })
        for id in ids:
            print('Node {} is alive'.format(id))
        if len(ids) == len(hosts):
            print('All nodes are alive')

    def do_sst(self, args):
        communication.broadcast(hosts, 'load-senario', { 'command': 'load ' + args })
        communication.broadcast(hosts, 'load-senario', { 'command': 'run'})
    
    def do_mine(self, args):
        print(communication.broadcast(hosts, 'load-senario', { 'command': 'mining'}))

    def do_stats(self, args):
        stats = communication.broadcast(hosts, 'get-stats', { })
        min_time = stats[0]['tsx'][settings.N-1][0]
        max_time = stats[0]['blc'][-1][0]
        trx = 0
        res2 = []
        for stat in stats:
            print(stat['id'])
            print(stat['tsx'][settings.N-1],stat['blc'][-1])
            print(len(stat['tsx'][settings.N-1:]),len(stat['vtsx'][settings.N-1:]),stat['ptsx'])
            print(stat['blc'][-1][0] - stat['tsx'][settings.N-1][0])

            res2.append(sum([x for x,_,_ in stat['mblc']]) / len(stat['mblc']))            

            trx += stat['ptsx']
            if stat['tsx'][settings.N-1][0] < min_time:
                min_time = stat['tsx'][settings.N-1][0]
            if stat['blc'][-1][0] >  max_time:
                max_time = stat['blc'][-1][0]
        
        res = trx / (max_time - min_time)

        print('The result for throuhput is: {}'.format(res))
        print('The result for block is: {}'.format(res2))

        
if __name__ == '__main__':
    hosts = communication.unicast_bootstrap('management', { 'command': 'hosts' })
    RouterShell(hosts).cmdloop()