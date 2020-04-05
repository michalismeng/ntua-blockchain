import { Action } from '@ngrx/store';
import { Node } from 'src/models/node';
import { Error } from 'src/models/error';

export enum SystemActionTypes {
    SetSystemState = '[System] Set system state',

    SetBootstrapAddress = '[System] Set bootstrap address',

    KillSystem = '[System] Kill Noobcash',

    KillSystemSuccess = '[System] Kill Noobcash Success',

    GetConfiguration = '[System] Get configuration',
    GetConfigurationSuccess = '[System] Get configuration success',
    GetConfigurationFailure = '[System] Get configuration failure',

}

export class SetSystemState implements Action {
    readonly type = SystemActionTypes.SetSystemState;

	constructor(public newState: string) {}
}

export class SetBootstrapAddress implements Action {
    readonly type = SystemActionTypes.SetBootstrapAddress;

	constructor(public bootstrap_ip: string, public bootstrap_port: number) {}
}

export class KillSystem implements Action {
    readonly type = SystemActionTypes.KillSystem;
	constructor() {}
}

export class KillSystemSuccess implements Action {
    readonly type = SystemActionTypes.KillSystemSuccess;

	constructor() {}
}

export class GetConfiguration implements Action {
    readonly type = SystemActionTypes.GetConfiguration;

	constructor(public bootstrap_ip: string, public bootstrap_port: number) {}
}

export class GetConfigurationSuccess implements Action {
    readonly type = SystemActionTypes.GetConfigurationSuccess;

	constructor(public configuration: {N: number, capacity: number, difficulty: number}) {}
}

export class GetConfigurationFailure implements Action {
    readonly type = SystemActionTypes.GetConfigurationFailure;

	constructor(public errorMessage: Error) {}
}

export type All = 
    | SetSystemState
    | SetBootstrapAddress
    | KillSystem
    | KillSystemSuccess
    | GetConfiguration
    | GetConfigurationSuccess
    | GetConfigurationFailure
    ;