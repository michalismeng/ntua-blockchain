import { Injectable } from '@angular/core';
import { Actions, Effect, ofType } from '@ngrx/effects';
import { Observable } from 'rxjs';
import { tap, map, filter, delay } from 'rxjs/operators';
import { Store } from '@ngrx/store';
import { AppState } from '../reducers';
import { SystemActionTypes, KillSystemSuccess, GetConfigurationSuccess } from '../actions/system.actions';
import { ConfigService } from 'src/services/config.service';
import { GetHostsFailure, GetHostsSuccess } from '../actions/node.actions';
import { Error } from 'src/models/error';


@Injectable()
export class SystemEffect {

  @Effect({ dispatch: false })
  KillSystem: Observable<any> = this.actions$.pipe(
    ofType( SystemActionTypes.KillSystem ),
    tap(_ => this.configService.killAll().subscribe())
  )

  @Effect({ dispatch: false })
  GetConfiguration: Observable<any> = this.actions$.pipe(
    ofType( SystemActionTypes.GetConfiguration ),
    tap(a => {
      this.configService.getConfig(a.bootstrap_ip, a.bootstrap_port).subscribe(
          config => this.store.dispatch(new GetConfigurationSuccess(config)),
          error => this.store.dispatch(new GetHostsFailure(new Error(error.message, error.error))))
    }))


  constructor(private actions$: Actions, private configService: ConfigService, private store: Store<AppState>) { }

}
