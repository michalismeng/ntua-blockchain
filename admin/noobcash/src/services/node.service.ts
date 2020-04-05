import { Injectable } from '@angular/core';
import { Observable, throwError, of } from 'rxjs';
import { HttpClient, } from '@angular/common/http';
import { map, tap } from 'rxjs/operators';
import { Command } from 'src/models/command';
import { Node } from 'src/models/node';
import { environment as env} from 'src/environments/environment'

@Injectable()
export class NodeService {

    private readonly serverUrl = env.serverUrl

    constructor(protected http: HttpClient) { }

    public pingHost(ip: string, port: number): Observable<{ 'id': number, 'ip': string, 'port': number}> {
        let command = new Command([[ip, port]], `management`, 'echo-id')
        return this.http.post<[number, string, number][]>(`${this.serverUrl}/forward-command`, { payload: command })
            .pipe(
                map(res => res[0]),
                map(id => { return { 'id': id[0], 'ip': id[1], 'port': id[2] }} )
            );
    }

    public getHosts(bootstrap_ip: string, bootstrap_port: number) {
        let command = new Command([[bootstrap_ip, bootstrap_port]], 'management', 'hosts')
        return this.http.post<[string, number][]>(`${this.serverUrl}/forward-command`, { payload: command })
            .pipe(
                map(res => res[0]),
                map(hs => hs.map(h => { return { 'ip': h[0], 'port': h[1]}}))
            )
    }

    public getBalance(node: Node) {
        let command = new Command([[node.ip, node.port]], 'management', 'balance')
        return this.http.post<[number, [number, number][]][]>(`${this.serverUrl}/forward-command`, { payload: command })
            .pipe(
                map(res => res[0][1]),
                map(res => res.map(r => { return { 'id': r[0], 'balance': r[1]} })),
            )
    }

    public getIsMining(node: Node): Observable<boolean> {
        let command = new Command([[node.ip, node.port]], 'management', 'mining')
        return this.http.post<boolean[]>(`${this.serverUrl}/forward-command`, { payload: command })
            .pipe(
                map(res => res[0]),
            )
    }

    public doTransaction(sourceID: number, targetID: number, amount: number, nodes: Node[]) {
        let args = `exec id${sourceID} t ${targetID} ${amount}`
        let command = new Command(nodes.map(n => [n.ip, n.port]), 'execute-command', args)
        return this.http.post(`${this.serverUrl}/forward-command`, { payload: command })
    }

    public pingNodes(nodes: Node[]): Observable<{ 'id': number, 'ip': string, 'port': number}[]> {
        let command = new Command(nodes.map(n => [n.ip, n.port]), `management`, 'echo-id', true)
        return this.http.post<[number, string, number][]>(`${this.serverUrl}/forward-command`, { payload: command })
            .pipe(
                map(res => res.map(id => { return { 'id': id[0], 'ip': id[1], 'port': id[2] }}) ),
            );
    }

    public getBalances(nodes: Node[]) {
        let command = new Command(nodes.map(n => [n.ip, n.port]), 'management', 'balance', true)
        return this.http.post<[number, [number, number][]][]>(`${this.serverUrl}/forward-command`, { payload: command })
            .pipe(
                map(res => res.map(r => { return { id: r[0], balances: r[1] } })),
                map(res => res.map(r => { return { id: r.id, balances: r.balances.map(_r => { return { 'id': _r[0], 'balance': _r[1]} } ) }})),
            )
    }
}