import Tester, { BaseTester, TesterError } from "../../my_modules/tester";
import axios, { AxiosRequestConfig, AxiosResponse,  } from "axios";

interface TesterHttpRequestExpect {
    statusCode?: number,
    headers?: {
        keys?: Array<string>,
        values?: any
    },
    body?: {
        raw?: string,
        jsonKeys?: Array<string>,
        jsonValues?: any
    }
}

interface TesterHttpRequestArg {
    url: string;
    method?: string;
    auth?: any;
    expectation?: TesterHttpRequestExpect;
    praReq?: () => void
}

function objectGet(object: any, keys: Array<string>): any|undefined{
    const key = keys.shift()
    if (key== undefined) return undefined
    let subObject = object[key]
    if (keys.length == 0){
        return subObject
    }
    else if (subObject == undefined ) return undefined
    else return objectGet(subObject, keys)
}

class TesterHttpRequest extends BaseTester implements Tester {
    static baseUrl: string = "http://localhost:3000/";
    private arg: TesterHttpRequestArg;

    constructor(name: string, arg: TesterHttpRequestArg){
        super();
        this.name = name
        this.arg = arg
    }

    config(): AxiosRequestConfig {
        let config: AxiosRequestConfig = {
            baseURL: TesterHttpRequest.baseUrl,
            url: this.arg.url,
            responseType: 'text',
        }
        switch (this.arg.method) {
            case "get":
                config.method = "get"
                break;
            case "post":
                config.method = "post"
                break;
        
            default:
                break;
        }

        if(this.arg.auth != undefined) {
            if (this.arg.auth.token != undefined)
                config.headers = {"Authorization": "bearer "+this.arg.auth.token}
            else if (this.arg.auth.username != undefined && this.arg.auth.password != undefined)
                config.auth = this.arg.auth
        }
        return config
    }

    expectSuccess(response: AxiosResponse<any>){
        if (this.arg.expectation == undefined) return
        let myExpect = this.arg.expectation

        // check status code
        if (myExpect.statusCode && myExpect.statusCode != response.status){
            throw new TesterError("StatusCode not match. Got "+response.status+" want "+ myExpect.statusCode);
            
        }

        // check header
        if (myExpect.headers) {
            if ( myExpect.headers.keys ){
                for(const headerKey of myExpect.headers.keys) {
                    if (response.headers[headerKey.toLowerCase()] == undefined)
                        throw new TesterError("Header", headerKey, "not exist");
                }
            }
            if ( myExpect.headers.values ){
                for(const headerKey in myExpect.headers.values) {
                    const headerValue = response.headers[headerKey.toLowerCase()]
                    const headerValueExpect = myExpect.headers.values[headerKey]
                    if (headerValue == undefined)
                        throw new TesterError("Header", headerKey, "not exist");
                    if (headerValue != headerValueExpect)
                        throw new TesterError("Header",headerKey,"not match. Got", headerValue, ". Want", headerValueExpect);
                }
            }
        }

        // check body
        if (myExpect.body) {
            if (myExpect.body.raw)
                if (response.data != myExpect.body.raw)
                    throw new TesterError("Body not match. Got", response.data, ". Want", myExpect.body.raw);

            if (myExpect.body.jsonKeys) {
                for (const k of myExpect.body.jsonKeys) {
                    let keys = k.split(".");
                    if (objectGet(response.data, keys) == undefined)
                        throw new TesterError("Body json key",k,"is not exists");
                }
            }

            if (myExpect.body.jsonValues) {
                for (const k in myExpect.body.jsonValues) {
                    let keys = k.split(".");
                    const jsonValue = objectGet(response.data, keys)
                    if (jsonValue != myExpect.body.jsonValues[k])
                        throw new TesterError(
                            "Body json key",k,"is not match. Got",jsonValue,
                            ". Want",  myExpect.body.jsonValues[k]
                        )
                }
            }
        }
    }

    expectError(status: number){
        if (this.arg.expectation == undefined) return
        let myExpect = this.arg.expectation

        // check status error
        if (!myExpect.statusCode || myExpect.statusCode != status){
            throw new Error("StatusCode error. Got "+status);
            
        }
    }

    async testFunc(){
        try {
            let response = await axios.request(this.config())
            this.expectSuccess(response)
        } catch (error) {
            if (error.response) {
                // The request was made and the server responded with a status code
                // that falls out of the range of 2xx
                this.expectError(error.response.status)
            } else {
                throw error;
            }
        }
    }
}

export default TesterHttpRequest