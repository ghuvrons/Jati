import Tester, { BaseTester } from "../../my_modules/tester";
import axios from "axios";

class TesterHttpRequest extends BaseTester implements Tester {
    constructor(name: string){
        super();
        this.name = name
    }

    async testFunc(){
        this.log("wok")
    }
}

export default TesterHttpRequest