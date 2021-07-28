import Tester, { BaseTester, TesterRunner } from "../my_modules/tester"
import { TesterHttpRequest } from "./tester";
import * as gg from './test_data/http-request.json';

var testers: Array<Tester> = [];
gg.forEach(jsonTester => {
    let tester = new TesterHttpRequest(jsonTester.name)
    testers.push(tester)
});

TesterRunner.run(testers).then((r)=>{
    
})