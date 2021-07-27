import re, inspect, pprint
from Jati.Base.Log import Log
from Jati.Base.Controller import Controller as JatiBaseController
from Jati.Base.Middleware import Middleware as JatiBaseMiddleware

class Route:

    # generate route for prefix url with normal format (it contains default value)
    def group(self, *arg, **args):
        obj = {'url':'/', 'middleware':[], 'group':[], 'error': None}
        obj.update(args)
        return {
            'url': str(obj['url']), 
            'middleware': obj['middleware'], 
            'errorHandler': obj['error'], 
            'sub': [x for x in obj['group']]
        }

    # generate route for end node route with normal format (it contains default value)
    def route(self, *arg, **args):
        # key "respond" for ws route
        obj = {
            'url':'/', 'controller':None, 'method':['get', 'post'], 'middleware':[], 'respond':None, 'error': None
        }
        obj.update(args)
        return {
            'url': str(obj['url']), 
            'controller': str(obj['controller']), 
            'methods': obj['method'], 
            'middleware': obj['middleware'], 
            'errorHandler': obj['error'], 
            "respond": obj['respond'] if not obj['respond'] else str(obj['respond'])
        }

    # objToRoute convert objs tree object as our format
    def objToRoute(self, objs):
        result = []
        for obj in objs:
            if 'group' in obj:
                obj['group'] = self.objToRoute(obj['group'])
                result.append(self.group(**obj))
            else:
                result.append(self.route(**obj))
        return result

class Router:
    def __init__(self):
        self.methods = {
            #"get": {"controller": ..., middleware: []},
            #"post": {},
            #"ws": {},
            'errorHandler': None
        }
        self.sub = {
            #"sub_url": router
        }
        self.sub_regrex = [
            #(regex, variables, router, ) # regex = reroute
        ]
    
    # search url nestedly in router tree
    # return tuple : (middleware, controller, data if regex router, errorHandler, and respond event if websocket route)
    def search(self, url, method='get', isGetRespond = False, errorHandler = None):
        if type(url) == str:
            method = method.lower()
            url = url.split('/')
            while True:
                try:
                    url.remove('')
                except:
                    break
        if self.methods["errorHandler"]:
            errorHandler = self.methods["errorHandler"]

        tmp = ([], None, {}, errorHandler)
        if len(url) == 0:
            if method in self.methods:
                tmp = (
                    self.methods[method]['middleware'], 
                    self.methods[method]['controller'], 
                    {}, 
                    errorHandler
                )
                if isGetRespond:
                    return tmp + (self.methods[method]['respond'], )
                else:
                    return tmp
            else: return tmp + (None,) if isGetRespond else tmp
        
        current_url = url.pop(0)
        if current_url in self.sub:
            result = self.sub[current_url]["router"].search(url, method, isGetRespond, errorHandler)
            return result

        for regex,variables,_router in self.sub_regrex:
            matchObj = re.match('^'+regex+'$', current_url)
            if matchObj:
                data = {}
                i = 0
                for key in variables:
                    i+=1
                    data[key] = matchObj.group(i)
                result = _router.search(url, method, isGetRespond, errorHandler)
                if result[1]: #found
                    result[2].update(data)
                return result
        return tmp + (None,) if isGetRespond else tmp
    
    # createRoute create new Router child
    def createRoute(self, url, methods, controller, middleware, errorHandler = None, respond = None):
        if len(url) == 0:
            self.methods['errorHandler'] = errorHandler
            for method in methods:
                method = method.lower()
                if not method in self.methods:
                    self.methods[method] = {
                        'controller': controller, 
                        'middleware': [], 
                        'respond': respond
                    }
                for mw in self.methods[method]['middleware']:
                    if mw in middleware:
                        middleware.remove(mw)
                self.methods[method]['middleware'].extend(middleware)
        else: 
            current_url = url.pop(0)
            if re.search(r'{[^{}?]+\??([^{}]+({\d+\,?\d*})?)*}', current_url):
                
                def dashrepl(matchobj):
                    m = re.match(r"{[^{}?]+\?((?:[^{}]+(?:{\d+\,?\d*})?)+)}", matchobj.group(0))
                    if m:
                        return '('+m.group(1).replace('(', '(?:')+')'
                    else:
                        return '(.*)'
                def replaceSpesChar(s):
                    spesChar = ['(',')','[',']','<','>','?','+','\\','*','.','!','$','^','|']
                    level = 0
                    result = ''
                    for c in s:
                        if c == '{': level+=1
                        elif c == '}': level-=1
                        if level==0 and c in spesChar:
                            result += '\\'
                        result += c
                    return result
                regex_current_url = replaceSpesChar(current_url)
                revar = re.sub(r'{[^{}?]+\??([^{}]+({\d+\,?\d*})?)*}', '{([^{}?]+)\??(?:[^{}]+(?:{\\\d+\,?\\\d*})?)*}', regex_current_url)
                variables = []
                m = re.match(r'^'+revar+'$', current_url)
                if m:
                    i = 0
                    while True:
                        try:
                            i+=1
                            variables.append(m.group(i))
                        except:
                            break
                regex = re.sub(r'{[^{}?]+\??([^{}]+({\d+\,?\d*})?)*}', dashrepl, regex_current_url)
                tmp = (regex, variables, Router())
                self.sub_regrex.append(tmp)
                tmp[2].createRoute(url, methods, controller, middleware, errorHandler, respond)
            else:
                if not current_url in self.sub:
                    self.sub[current_url] = {"router": Router(), "errorHandler": errorHandler}
                self.sub[current_url]["router"].createRoute(url, methods, controller, middleware, errorHandler, respond)

# Every Jati App has 2 BaseRoute instance. There are for http route and ws route.
# see App class for detail
class BaseRoute:
    controllerCache = {}
    middlewareCache = {}

    def __init__(self, app_module, isWsRoute = False, log:Log=None):
        self.router = Router() # this is main router
        self.isWsRoute = isWsRoute
        self.Controller = app_module.Controller
        self.Middleware = app_module.Middleware
        self.Databases = {}
        self.Models = {}
        self.Modules = {}
        self.Services = {}
        self.appPath = app_module.__path__[0]
        self.log = log

    # print router as object
    def print(self):
        pprint.pprint(self.routerToObject(self.router))
        pass 

    def routerToObject(self, router: Router, url = '/'):
        result = {
            "url": url,
            "methods": router.methods,
            "sub" : []
        }
        for url in router.sub.keys():
            result['sub'].append(self.routerToObject(router.sub[url]["router"], url))
        return result

    # generateRoute is alias of "group"
    def generateRoute(self, route_config):
        self.group(route_config)

    # group will generate router tree from route_config
    # route_config is array tree of Route data. see Route class
    def group(self, route_config, parent_url = '/', conf_middleware=[], errorHandler = None):
        for conf in route_config:
            if "errorHandler" in conf and conf['errorHandler']:
                errorHandler = self.controllerToCallable(conf['errorHandler'])
            if "controller" in conf:
                url_arr = (parent_url+'/'+conf['url']).split('/')
                while True:
                    try:
                        url_arr.remove('')
                    except:
                        break

                controller = self.controllerToCallable(conf['controller'])
                middleware = []
                for mw in conf_middleware+conf['middleware']:
                    mw = self.middlewareToCallable(mw)
                    if mw not in middleware:
                        middleware.append(mw)
                self.router.createRoute(url_arr, conf['methods'], controller, middleware, errorHandler, conf['respond'])
            elif "sub" in conf:
                self.group(
                    conf['sub'], 
                    (parent_url+'/'+conf['url']), 
                    conf_middleware+(conf['middleware'] if 'middleware' in conf else []),
                    errorHandler
                )
    
    # controllerToCallable can return None callable function or instance of controller
    def controllerToCallable(self, controller):
        if type(controller) == str:
            controller = controller.split('@', 1)
            controller_class_name = controller[0].split('/')
            if not controller[0] in self.controllerCache:
                controller_class = None
                # try search controller class in Apps
                try:
                    controller_class = self.Controller
                    for c_class_name in controller_class_name:
                        controller_class = getattr(controller_class, c_class_name)
                except AttributeError:
                    controller_class = None

                # try search controller class in dependencies
                if controller_class is None:
                    try:
                        for c_class_name in controller_class_name:
                            if controller_class is None:
                                controller_class = __import__(c_class_name)
                            else:
                                controller_class = getattr(controller_class, c_class_name)
                    except (AttributeError, ModuleNotFoundError):
                        controller_class = None
                        
                if controller_class and hasattr(controller_class,'__mro__') and JatiBaseController in inspect.getmro(controller_class):
                    controller_class.appPath = self.appPath
                    controller_class.Databases = self.Databases
                    controller_class.Models = self.Models
                    controller_class.Services = self.Services
                    self.controllerCache[controller[0]] = controller_class()
                elif self.log:
                    self.log.error("Controller (%s) not found. Check your router json", controller[0])

            if controller[0] in self.controllerCache:
                if len(controller) > 1:
                    return getattr(self.controllerCache[controller[0]], controller[1])
                else:
                    # controller as handler
                    return self.controllerCache[controller[0]]

        elif callable(controller):
            return controller
        return None

    def middlewareToCallable(self, middleware):
        if type(middleware) is str:
            middleware = middleware.split('@', 1)
            middleware_class_name = middleware[0].split('/')
            if not middleware[0] in self.middlewareCache:
                middleware_class = None

                # try search middleware class in Apps
                try:
                    middleware_class = self.Middleware
                    for mw_class_name in middleware_class_name:
                        middleware_class = getattr(middleware_class, mw_class_name)
                except AttributeError:
                    middleware_class = None

                # try search middleware class in dependencies
                if middleware_class is None:
                    try:
                        for mw_class_name in middleware_class_name:
                            if middleware_class is None:
                                middleware_class = __import__(mw_class_name)
                            else:
                                middleware_class = getattr(middleware_class, mw_class_name)
                    except (AttributeError, ModuleNotFoundError):
                        middleware_class = None

                if middleware_class and hasattr(middleware_class,'__mro__') and JatiBaseMiddleware in inspect.getmro(middleware_class):
                    middleware_class.appPath = self.appPath
                    middleware_class.Databases = self.Databases
                    middleware_class.Models = self.Models
                    middleware_class.Services = self.Services
                    self.middlewareCache[middleware[0]] = middleware_class()
                elif self.log:
                    self.log.error("Middleware (%s) not found. Check your router json.", middleware[0])

            if middleware[0] in self.middlewareCache and len(middleware) > 1:
                return getattr(self.middlewareCache[middleware[0]], middleware[1])

        elif callable(middleware):
            return middleware
        return None