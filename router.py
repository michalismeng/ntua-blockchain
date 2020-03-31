#!/usr/bin/env python3

import requests
import communication
import settings
import cmd, sys
import time

ips = settings.N * ['127.0.0.1']
ports = [25000 + i for i in range(settings.N)]
hosts = list(zip(ips, ports))


class RouterShell(cmd.Cmd):
    intro = 'Welcome to noobcoin\n'
    prompt = '(client) '

    def do_load(self, args):
        file = args.split()[0]
        command = 'load {}'.format(file)
        communication.broadcast(hosts, 'execute-command', { 'command': command })

    def do_exec(self, args):
        print(args)
        communication.broadcast(hosts, 'execute-command', { 'command': 'exec' + args })

    def do_next(self, args):
        communication.broadcast(hosts, 'execute-command', { 'command': 'next' })

    def do_run(self, args):
        file = args.split()[0]
        print('running file', file)
        self.do_load(file)
        with open('scripts/{}'.format(file), 'r') as f:
            commands_script = [x.strip() for x in f.readlines()] 
            count = len(commands_script)
            print('executig {} commands'.format(count))

        for i in range(count):
            print('executing: {}'.format(commands_script[i]))
            self.do_next('')
            time.sleep(0.5)

    def do_script(self, args):
        communication.broadcast(hosts, 'load-senario', { 'command': 'load ' + args })
    
    def do_start(self, args):
        communication.broadcast(hosts, 'load-senario', { 'command': 'run'})
    
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
    RouterShell().cmdloop()