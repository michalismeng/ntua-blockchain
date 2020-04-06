import { Injectable } from '@angular/core';
import { Actions, Effect, ofType } from '@ngrx/effects';
import { Observable } from 'rxjs';
import { tap, map, filter } from 'rxjs/operators';
import { Store } from '@ngrx/store';
import { AppState } from '../reducers';
import { NodeService } from 'src/services/node.service';
import { NodeActionTypes, GetHostsSuccess, GetHostsFailure, PingNodeSuccess, PingNodeFailure, GetBalanceSuccess, GetBalanceFailure, GetMiningSuccess, PingAllNodeSuccess, GetAllBalanceSuccess, GetAllMiningSuccess} from '../actions/node.actions';
import { Node } from 'src/models/node'; 
import { Error } from 'src/models/error';


@Injectable()
export class NodeEffect {

  @Effect({ dispatch: false })
  GetHosts: Observable<any> = this.actions$.pipe(
    ofType( NodeActionTypes.GetHosts ),
    tap(a => {
      this.nodeService.getHosts(a.bootstrap_ip, a.bootstrap_port)
        .pipe(
            map(hs => hs.map((h, idx) => new Node(idx, h.ip, h.port, undefined, undefined, undefined)))
        ).subscribe(
          nodes => this.store.dispatch(new GetHostsSuccess(nodes)),
          error => this.store.dispatch(new GetHostsFailure(new Error(error.message, error.error))))
    }))

  @Effect({ dispatch: false })
  PingNode: Observable<any> = this.actions$.pipe(
    ofType( NodeActionTypes.PingNode ),
    tap(a => {
      this.nodeService.pingHost(a.ip, a.port).subscribe(
          res => this.store.dispatch(new PingNodeSuccess(res)),
          error => this.store.dispatch(new PingNodeFailure({ ip: a.ip, port: a.port })))
    }))

  @Effect({ dispatch: false })
  GetBalance: Observable<any> = this.actions$.pipe(
    ofType( NodeActionTypes.GetBalance ),
    tap(a => {
      this.nodeService.getBalance(a.node).subscribe(
          balances => this.store.dispatch(new GetBalanceSuccess(a.node.id, balances)),
          error => this.store.dispatch(new GetBalanceFailure(new Error(error.message, error.error))))
    }))

  @Effect({ dispatch: false })
  GetMining: Observable<any> = this.actions$.pipe(
    ofType( NodeActionTypes.GetMining ),
    tap(a => {
      this.nodeService.getIsMining(a.node).subscribe(
          ([id, mining]) => this.store.dispatch(new GetMiningSuccess(id, mining)),
          error => this.store.dispatch(new GetBalanceFailure(new Error(error.message, error.error))))
    }))

  @Effect({ dispatch: false })
  PingAllNodes: Observable<any> = this.actions$.pipe(
    ofType( NodeActionTypes.PingAllNodes ),
    tap(a => {
      this.nodeService.pingNodes(a.nodes).subscribe(
          res => this.store.dispatch(new PingAllNodeSuccess(res)),
          error => console.log(error))
    }))

  @Effect({ dispatch: false })
  GetBalances: Observable<any> = this.actions$.pipe(
    ofType( NodeActionTypes.GetAllBalance ),
    tap(a => {
      this.nodeService.getBalances(a.nodes).subscribe(
          balances => this.store.dispatch(new GetAllBalanceSuccess(balances)))
    }))

  @Effect({ dispatch: false })
  GetMinings: Observable<any> = this.actions$.pipe(
    ofType( NodeActionTypes.GetAllBalance ),
    tap(a => {
      this.nodeService.getAllMining(a.nodes).subscribe(
          minings => this.store.dispatch(new GetAllMiningSuccess(minings)))
    }))

 

  constructor(private actions$: Actions, private store: Store<AppState>, private nodeService: NodeService) { }

}
