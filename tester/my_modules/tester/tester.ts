// class Tester {
//     static fromJson(): Tester {
//         var tester = new Tester()
//         return tester
//     }
// }
interface Tester {
    name: string;
    error: string | undefined;
    run: () => Promise<void>,
}

class BaseTester {
    public name: string;
    public error: string | undefined;

    constructor(name: string) {
        this.name = name
    }
}

export { BaseTester }
export default Tester;