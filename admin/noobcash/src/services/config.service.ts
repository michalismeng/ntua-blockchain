import { Injectable } from '@angular/core';
import { HttpClient, } from '@angular/common/http';
import { environment as env} from 'src/environments/environment'
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { Command } from 'src/models/command';

@Injectable()
export class ConfigService {
    constructor(protected http: HttpClient) { }

    public setupAll(N: number, capacity: Number, difficulty: number) {
        return this.http.post(`${env.serverUrl}/setup-all`, { payload: { 'N': N, 'capacity': capacity, 'difficulty': difficulty } })
    }

    public killAll() {
        return this.http.post(`${env.serverUrl}/kill-all`, { })
    }

    public getConfig(bootstrap_ip: string, bootstrap_port: number): Observable<{'N': number, 'capacity': number, 'difficulty': number}> {
        let command = new Command([[bootstrap_ip, bootstrap_port]], 'management', 'config')
        return this.http.post<[number, number, number]>(`${env.serverUrl}/forward-command`, { payload: command })
            .pipe(
                map(res => res[0]),
                map(c => { return { 'N': c[0], 'capacity': c[1], 'difficulty': c[2]}}))
    }
}