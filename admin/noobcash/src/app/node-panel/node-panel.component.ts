import { Component, OnInit, Input } from '@angular/core';
import { Observable, combineLatest, merge, of } from 'rxjs';
import { map, withLatestFrom, startWith, filter, tap } from 'rxjs/operators';
import { Store } from '@ngrx/store';
import { AppState } from '../reducers';
import { GetBalance, PingNode, GetMining } from '../actions/node.actions';
import { Node } from 'src/models/node';

@Component({
  selector: 'app-node-panel',
  templateUrl: './node-panel.component.html',
  styleUrls: ['./node-panel.component.css']
})
export class NodePanelComponent implements OnInit {

  @Input() nodeID: number;

  public node: Node;

  public canRefresh$: Observable<boolean>;

  getBalanceForCurrentNode() {
    let b = this.node.allBalances && this.node.allBalances.find(b => b.id == this.node.id) || null
    return b && b.balance || '-'
  }

  getMiningForCurrentNode() {
    if (this.node.isMining == null)
      return '-'
    return this.node.isMining
  }

  constructor(
    private store: Store<AppState>,
  ) {
    this.canRefresh$ = of(true)
    // this.canGetBalance$ = merge(
    //   of(false),
    //   combineLatest(
    //     this.store.select(s => s.system.configuration),
    //     this.store.select(s => s.nodes.nodes)
    //   ).pipe(
    //     filter(([c, n]) => c != null && n != null),
    //     map(([c, n]) => c.N == n.length)
    //   )
    // )
  }

  ngOnInit() {
    this.store.select(s => s.nodes.nodes)
      .pipe(map(ns => ns.find(n => n.id == this.nodeID)))
      .subscribe(n => this.node = n)
  }

  getBalance() {
    this.store.dispatch(new GetBalance(this.node))
  }

  getIsMining() {
    this.store.dispatch(new GetMining(this.node))
  }

  pingNode() {
    this.store.dispatch(new PingNode(this.node.ip, this.node.port))
  }
}
