import Tester, { BaseTester, TesterRunner, TesterError } from "../my_modules/tester";
import { TesterHttpRequest } from "./tester";
import test_data from './test_data/http-request.json';

// initiate data
var testers: Array<Tester> = [];
let i = 0
test_data.forEach(jsonTester => {
    let tester = new TesterHttpRequest("Test Request #"+(i++))
    testers.push(tester)
});

TesterRunner.run(async (t:Tester) => {
    await t.run("tes1", async () => {
        await t.run("tes1a", async () => {
            throw new Error("Whoops!");
        })
    })
    testers.forEach(tester => {
        t.run(tester.name, tester)
    });
})
.then((r)=>{
    
})