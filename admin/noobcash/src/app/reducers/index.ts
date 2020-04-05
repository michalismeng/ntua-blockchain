import { ActionReducerMap, MetaReducer } from '@ngrx/store';
import { environment } from '../../environments/environment';
import * as Nodes from './nodes.reducers';
import * as System from './system.reducers';



export interface AppState {
    nodes: Nodes.State,
    system: System.State
}

export const reducers: ActionReducerMap<AppState> = {
    nodes: Nodes.reducer,
    system: System.reducer
};

export const metaReducers: MetaReducer<AppState>[] = !environment.production ? [] : [];
