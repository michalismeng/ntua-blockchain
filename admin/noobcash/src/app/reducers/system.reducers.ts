import { All, SystemActionTypes } from '../actions/system.actions'
import { interval, Observable } from 'rxjs';
import { environment as env } from 'src/environments/environment'; 


export interface State {
    systemState: string;
    systemOrdinal: number,

    configuration: { N: number, capacity: number, difficulty: number };

    bootstrap: { ip: string, port: number }
    bootstrapAlive: boolean;

    errorMessage: string;
}

const initialState: State = {
    systemState: 'init',
    systemOrdinal: mapStateToOrdinal('init'),

    configuration: null,

    bootstrapAlive: false,
    bootstrap: { ip: env.production ? '192.168.1.3' : '127.0.0.1', port: 25000 },

    errorMessage: null
};

function mapStateToOrdinal(state: string) {
    switch(state) {
        case 'down': return -1;
        case 'init': return 0;
        case 'up': return 1;
        case 'quorum': return 2;
    }
    return -10;
}


export function reducer(state = initialState, action: All) {
    switch(action.type) {
        case SystemActionTypes.GetConfigurationSuccess:
            return Object.assign({}, state, { configuration: action.configuration, errorMessage: null });
        case SystemActionTypes.GetConfigurationFailure:
            return Object.assign({}, state, { configuration: null, errorMessage: action.errorMessage });

        case SystemActionTypes.SetSystemState:
            return Object.assign({}, state, { systemState: action.newState, systemOrdinal: mapStateToOrdinal(action.newState), errorMessage: null });

        // case SystemActionTypes.SetBootstrapAddress:
        //     let new_state = Object.assign({}, state, { ...initialState });
        //     return Object.assign({}, state, new_state, { bootstrap: { ip: action.bootstrap_ip, port: action.bootstrap_port } })

        case SystemActionTypes.KillSystemSuccess:
            return Object.assign({}, state, { ...initialState });

        default: return state;
    }
}