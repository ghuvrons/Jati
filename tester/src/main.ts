import Tester, { BaseTester, TesterRunner, TesterError } from "../my_modules/tester";
import { TesterHttpRequest } from "./tester";
import test_data from './test_data/http-request.json';

// initiate data
var testers: Array<Tester> = [];
let i = 0
test_data.forEach(jsonTester => {
    let tester = new TesterHttpRequest(jsonTester.name, jsonTester)
    testers.push(tester)
});

TesterRunner.run(async (t:Tester) => {
    // await t.run("tes1", async () => {
    //     await t.run("tes1a", async () => {
    //         throw new Error("Whoops!");
    //     })
    // })
    for(const tester of testers){
        await t.run(tester.name, tester)
    }
})
.then((r)=>{
    
})