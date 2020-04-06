import { Action } from '@ngrx/store';
import { Node } from 'src/models/node';
import { Error } from 'src/models/error';

export enum NodeActionTypes {

    GetHosts = '[Node] Get all hosts',
    GetHostsSuccess = '[Node] Get all hosts success',
    GetHostsFailure = '[Node] Get all hosts failure',

    GetBalance = '[Node] Get Balance',
    GetBalanceSuccess = '[Node] Get Balance Success',
    GetBalanceFailure = '[Node] Get Balance Failure',

    GetMining = '[Node] Get Mining',
    GetMiningSuccess = '[Node] Get Mining Success',
    GetMiningFailure = '[Node] Get Mining Failure',

    PingNode = '[Node] Ping Node',
    PingNodeSuccess = '[Node] Ping Node Success',
    PingNodeFailure = '[Node] Ping Node Failure',

    PingAllNodes = '[Node] Ping All Nodes',
    PingAllNodeSuccess = '[Node] Ping All Node Success',

    GetAllBalance = '[Node] Get All Balance',
    GetAllBalanceSuccess = '[Node] Get All Balance Success',

    GetAllMining = '[Node] Get All Mining',
    GetAllMiningSuccess = '[Node] Get All Mining Success',

}

export class GetHosts implements Action {
    readonly type = NodeActionTypes.GetHosts;

	constructor(public bootstrap_ip: string, public bootstrap_port: number) {}
}

export class GetHostsSuccess implements Action {
    readonly type = NodeActionTypes.GetHostsSuccess;

	constructor(public nodes: Node[]) {}
}

export class GetHostsFailure implements Action {
    readonly type = NodeActionTypes.GetHostsFailure;

	constructor(public errorMessage: Error) {}
}

export class PingNode implements Action {
    readonly type = NodeActionTypes.PingNode;

	constructor(public ip: string, public port: number) {}
}

export class PingNodeSuccess implements Action {
    readonly type = NodeActionTypes.PingNodeSuccess;

	constructor(public echo: { 'id': number, 'ip': string, 'port': number}) {}
}

export class PingNodeFailure implements Action {
    readonly type = NodeActionTypes.PingNodeFailure;

	constructor(public node_address: { 'ip': string, 'port': number}) {}
}

export class GetBalance implements Action {
    readonly type = NodeActionTypes.GetBalance;

	constructor(public node: Node) {}
}

export class GetBalanceSuccess implements Action {
    readonly type = NodeActionTypes.GetBalanceSuccess;

	constructor(public id, public balances: { id: number, balance: number }[]) {}
}

export class GetBalanceFailure implements Action {
    readonly type = NodeActionTypes.GetBalanceFailure;

	constructor(public errorMessage: Error) {}
}

export class GetMining implements Action {
    readonly type = NodeActionTypes.GetMining;

	constructor(public node: Node) {}
}

export class GetMiningSuccess implements Action {
    readonly type = NodeActionTypes.GetMiningSuccess;

	constructor(public id, public isMining: boolean) {}
}

export class GetMiningFailure implements Action {
    readonly type = NodeActionTypes.GetMiningFailure;

	constructor(public errorMessage: Error) {}
}

export class PingAllNodes implements Action {
    readonly type = NodeActionTypes.PingAllNodes;

	constructor(public nodes: Node[]) {}
}

export class PingAllNodeSuccess implements Action {
    readonly type = NodeActionTypes.PingAllNodeSuccess;

	constructor(public echo: { 'id': number, 'ip': string, 'port': number}[]) {}
}

export class GetAllBalance implements Action {
    readonly type = NodeActionTypes.GetAllBalance;

	constructor(public nodes: Node[]) {}
}

export class GetAllBalanceSuccess implements Action {
    readonly type = NodeActionTypes.GetAllBalanceSuccess;

	constructor(public balances: {id: number, balances: { id: number, balance: number }[] }[]) {}
}

export class GetAllMining implements Action {
    readonly type = NodeActionTypes.GetAllMining;

	constructor(public nodes: Node[]) {}
}

export class GetAllMiningSuccess implements Action {
    readonly type = NodeActionTypes.GetAllMiningSuccess;

	constructor(public minings: { id: number, mining: boolean}[]) {}
}

export type All = 
    | GetHosts
    | GetHostsSuccess
    | GetHostsFailure
    | PingNode
    | PingNodeSuccess
    | PingNodeFailure
    | GetBalance
    | GetBalanceSuccess
    | GetBalanceFailure
    | GetMining
    | GetMiningSuccess
    | GetMiningFailure
    | PingAllNodes
    | PingAllNodeSuccess
    | GetAllBalance
    | GetAllBalanceSuccess
    | GetAllMining
    | GetAllMiningSuccess
    ;