import { Node } from 'src/models/node'
import { All, NodeActionTypes } from '../actions/node.actions';
import { Error } from 'src/models/error';

export interface State {
    nodes: Node[];
    errorMessage: Error;
}

const initialState: State = {
    nodes: [],
    errorMessage: null
};


export function reducer(state = initialState, action: All) {
    switch(action.type) {
        case NodeActionTypes.GetHostsSuccess:
            return Object.assign({}, state, { nodes: action.nodes, errorMessage: null });
        case NodeActionTypes.GetHostsFailure:
            return Object.assign({}, state, { nodes: null, errorMessage: action.errorMessage });

        case NodeActionTypes.PingNodeSuccess:
            let _new_state = state

            if(_new_state.nodes.length) {
                let nodes: Node[] = JSON.parse(JSON.stringify(_new_state.nodes))
                nodes.find(n => n.id == action.echo.id).isAlive = true;
                _new_state = Object.assign({}, _new_state, { nodes: nodes, errorMessage: null });
            }

            return Object.assign({}, state, { ..._new_state })

        case NodeActionTypes.PingAllNodeSuccess:
            let new_nodes: Node[] = JSON.parse(JSON.stringify(state.nodes))
            new_nodes.forEach(n => n.isAlive = action.echo.find(nn => nn.id == n.id) != null)

            return Object.assign({}, state, { nodes: new_nodes })

        case NodeActionTypes.PingNodeFailure:
            let a_new_state = state

            if(a_new_state.nodes.length) {
                let nodes: Node[] = JSON.parse(JSON.stringify(a_new_state.nodes))
                nodes.find(n => n.ip == action.node_address.ip && n.port == action.node_address.port).isAlive = false;
                a_new_state = Object.assign({}, a_new_state, { nodes: nodes });
            }

            return Object.assign({}, state, { ...a_new_state })

        case NodeActionTypes.GetBalanceSuccess:

            let nodes: Node[] = JSON.parse(JSON.stringify(state.nodes))
            let node = nodes.find(n => n.id == action.id)
            node.allBalances = action.balances;

            return Object.assign({}, state, { nodes: nodes, errorMessage: null });

        case NodeActionTypes.GetBalanceFailure:
            return Object.assign({}, state, { errorMessage: action.errorMessage });

        case NodeActionTypes.GetMiningSuccess:

            let _nodes: Node[] = JSON.parse(JSON.stringify(state.nodes))
            _nodes.find(n => n.id == action.id).isMining = action.isMining

            return Object.assign({}, state, { nodes: _nodes, errorMessage: null });

        case NodeActionTypes.GetMiningFailure:
            return Object.assign({}, state, { errorMessage: action.errorMessage });

        case NodeActionTypes.GetAllBalanceSuccess:
            let _new_nodes: Node[] = JSON.parse(JSON.stringify(state.nodes))

            // set balances
            _new_nodes.forEach(n => { 
                let b = action.balances.find(nn => nn.id == n.id)
                n.allBalances = b && b.balances || null
            })

            // set liveness
            _new_nodes.forEach(n => n.isAlive = action.balances.find(nn => nn.id == n.id) != null)

            return Object.assign({}, state, { nodes: _new_nodes, errorMessage: null });

        default: return state;
    }
}