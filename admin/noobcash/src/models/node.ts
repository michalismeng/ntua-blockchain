
export class Node {
    constructor(
        public id: number,
        public ip: string,
        public port: number,
        public address: string,
        public isMining: boolean,
        public allBalances: { id: number, balance: number}[] = [],       // balance of all nodes of the network as viewed by this node
        public isAlive: boolean = false
    ) { }
}
