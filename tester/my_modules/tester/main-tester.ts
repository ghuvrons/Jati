import Tester, { BaseTester } from './tester'

class TesterResult {

}

class TesterRunner {
    static async run(testers: Array<Tester>): Promise<TesterResult>{
        let result = new TesterResult();
        for (let i = 0; i < testers.length; i++){
            await testers[i].run()
        }
        return result
    }
}

export default TesterRunner 