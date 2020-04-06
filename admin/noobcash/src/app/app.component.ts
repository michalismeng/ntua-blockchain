import { Component } from '@angular/core';
import { NodeService } from 'src/services/node.service';
import { Store } from '@ngrx/store';
import { AppState } from './reducers';
import { Observable, zip, interval, combineLatest, timer } from 'rxjs';
import { filter, withLatestFrom, delay, tap, map } from 'rxjs/operators';
import { SetSystemState, SetBootstrapAddress, GetConfiguration, KillSystem, KillSystemSuccess } from './actions/system.actions';
import { GetHosts, PingNode, PingAllNodes, GetAllBalance, GetHostsSuccess } from './actions/node.actions';

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
    ).subscribe(_ => this.store.dispatch(new SetSystemState('semi-quorum')) )

    // when semi-quorum ping all hosts to find out liveness
    combineLatest(
      this.store.select(s => s.system.systemState),
      this.store.select(s => s.nodes.nodes)
    ).pipe(filter(([s, n]) => s == 'semi-quorum' && n != null)).subscribe(([_, n]) => this.store.dispatch(new PingAllNodes(n)))

    combineLatest(
      this.store.select(s => s.system.systemState),
      this.store.select(s => s.nodes.nodes)
    ).pipe(filter(([s, ns]) => s == 'semi-quorum' && ns && ns.every(n => n.isAlive))).subscribe(([_, n]) => this.store.dispatch(new SetSystemState('quorum')))
    

    // when in quorum update all balances
    combineLatest(
      timer(0, 1000),
      this.store.select(s => s.system.systemState),
    ).pipe(
      filter(([_, s]) => s == 'semi-quorum' || s == 'quorum'),
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

    // when in quorum check if system is dead
    combineLatest(
      this.store.select(s => s.system.systemState),
      this.store.select(s => s.nodes.nodes)
    ).pipe(filter(([s, n]) => s == 'quorum' && n && n.every(n => !n.isAlive)), delay(1000))
    .subscribe(_ => {
      this.store.dispatch(new KillSystemSuccess())
      this.store.dispatch(new GetHostsSuccess([]))
    })
  }
}
