// class Tester {
//     static fromJson(): Tester {
//         var tester = new Tester()
//         return tester
//     }
// }
interface Tester {
    name: string;
    run: (name: string, t:Tester|(() => Promise<void>)) => Promise<void>,
    log: (...msg: any) => void;
    runTest: () => Promise<TesterResult>;
}

class BaseTester implements Tester{
    static isLog: boolean = true;
    static deep: number = 0;

    public name: string = "";

    async run(name: string, t:Tester|(() => Promise<void>)): Promise<void>{
        this.name = name
        if (typeof t === "function") {
            this.testFunc = t
        } else {
            this.runTest()
        }
        return 
    };

    async testFunc(): Promise<void> {}

    async runTest(): Promise<TesterResult>{
        let result = new TesterResult();
        this.log("[testing] ", this.name)

        BaseTester.deep++
        if(this.testFunc != undefined){
            let start = new Date();
            try{
                await this.testFunc()
            }
            catch(err){
                result.error = err
            }
            let end = new Date();
            result.executetime = end.getTime() - start.getTime();
        }
        BaseTester.deep--

        return result
    };

    log: (...msg: any) => void = BaseTester.log

    static log(...msg: any){
        let spaceStr = ""
        for(let i = 0; i < BaseTester.deep; i++) spaceStr += "  "
        if (BaseTester.isLog) {
            console.log(spaceStr, ...msg)
        }
    }
}

class TesterResult {
    public executetime: number = 0
    public error: TesterError | undefined

    constructor(){

    }

    print(){
        BaseTester.deep++
        BaseTester.log("[result] :")
        BaseTester.deep++
        if(this.error != undefined)
            BaseTester.log("error :", this.error.message)
        BaseTester.log("execute time :", this.executetime/1000, "s")
        BaseTester.deep -= 2
    }
}

class TesterError extends Error {
    constructor (...message: Array<string>) {
        super(message.join(' '));    
    }
}

export { BaseTester, TesterResult, TesterError }
export default Tester;