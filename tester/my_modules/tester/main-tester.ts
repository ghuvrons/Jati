import Tester, { BaseTester, TesterResult } from './tester'

class TesterRunner extends BaseTester implements Tester {
    name: string = "";

    constructor(){
        super();
    }
    async run(name: string, t:Tester|(() => Promise<void>)): Promise<void>{
        this.log("---------------------------------")
        if (typeof t === "function") {
            this.name = name
            this.testFunc = t
            let result = await this.runTest()
            result.print()
        } else {
            if (t.runTest != undefined){
                t.name = name
                let result = await t.runTest()
                result.print()
            }
        }
        this.log("---------------------------------")
        return 
    };

    static async run(f :(tester: Tester) => Promise<void>) : Promise<TesterResult>{
        let result = new TesterResult();
        let mainTester = new TesterRunner()
        await f(mainTester)
        return result
    }
}

export default TesterRunner 