
export class Command {
    constructor(
        public targetHosts: [string, number][],
        public api: string,
        public args: string,
        public ignoreException: boolean = false
    ) { }
}
