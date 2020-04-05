import { Component } from '@angular/core';
import { NodeService } from 'src/services/node.service';
import { Store } from '@ngrx/store';
import { AppState } from './reducers';
import { Observable, zip, interval, combineLatest, timer } from 'rxjs';
import { filter, withLatestFrom, delay, tap, map } from 'rxjs/operators';
import { SetSystemState, SetBootstrapAddress, GetConfiguration, KillSystem } from './actions/system.actions';
import { GetHosts, PingNode, PingAllNodes, GetAllBalance } from './actions/node.actions';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'noobcash';

  public systemState: number;

  constructor(
    private nodeService: NodeService,
    private store: Store<AppState>
  ){
    // let default_ip = env.production ? '192.168.1.3' : '127.0.0.1'
    // let default_port = 25000

    // Bootstrap address is locked
    // this.store.dispatch(new SetBootstrapAddress(default_ip, default_port))

    this.store.select(s => s.system.systemOrdinal).subscribe(o => this.systemState = o)

    // system is init or down -- ping bootstrap node every 1 second
    combineLatest(
      timer(0, 1000),
      this.store.select(state => state.system.bootstrap),
      this.store.select(state => state.system.systemOrdinal)
    ).pipe(filter(([_, _1, state]) => state <= 0))
    .subscribe(([_, boot, state]) => {
      this.nodeService.pingHost(boot.ip, boot.port).subscribe(
        _ => this.store.dispatch(new SetSystemState('up')),
        error => this.store.dispatch(new SetSystemState('down'))
      )
    })

    // system state is up -- wait for all nodes to join
    combineLatest(
      timer(0, 1000),
      this.store.select(state => state.system.bootstrap),
      this.store.select(s => s.system.systemState)
    ).pipe(filter(([_1, _2, state]) => state == 'up'))
    .subscribe(([_1, boot, _2]) => {
      this.store.dispatch(new GetHosts(boot.ip, boot.port))   // get hosts that appear in the bootstrap's ring
    })

    // check for quorum
    combineLatest(
      this.store.select(s => s.system.systemOrdinal),
      this.store.select(s => s.system.configuration),
      this.store.select(s => s.nodes.nodes)
    ).pipe(
      filter(([s, _, _1]) => s == 1),
      filter(([_, c, n]) => c && n && c.N == n.length),
    ).subscribe(_ => this.store.dispatch(new SetSystemState('quorum')) )
    

    // when in quorum update all balances
    combineLatest(
      timer(0, 1000),
      this.store.select(s => s.system.systemState),
    ).pipe(
      filter(([_, s]) => s == 'quorum'),
      withLatestFrom(this.store.select(s => s.nodes.nodes))
    ).subscribe(([_, nodes]) => this.store.dispatch(new GetAllBalance(nodes)))

    this.store.select(s => s.system.systemState)
      .pipe(
        filter(state => state == 'up'),
        withLatestFrom(this.store.select(state => state.system.bootstrap)),
      )
      .subscribe(([_, boot]) => {
        this.store.dispatch(new GetConfiguration(boot.ip, boot.port))
      })
  }
}
