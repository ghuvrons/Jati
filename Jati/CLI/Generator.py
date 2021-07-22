import os, json
from typing import List

class Generator:
    def __init__(self, site):
        if site is None:
            site = 'Site'
        if site[0] is not '/':
            site = './'+site
        self.site = site

    def generateProject(self):
        if not os.path.isdir(self.site):
            os.mkdir(self.site)
        if not os.path.isfile(self.site+'/__init__.py'):
            initF = open(self.site+'/__init__.py', "w")
            initF.write(self.templateConfig)
            initF.close()
        self.generateController("Welcome")
        self.generateMiddleware()
        self.generateDatabase()
        self.generateModel()
        self.generateService()
        self.generateAuth()
        self.generateRoute("/", "Welcome/Welcome@index")

    def generateController(self, name):
        dirCtrl = self.site+"/Controller"
        jsonCtrl = dirCtrl+'/controller.json'
        if not os.path.isdir(dirCtrl):
            os.mkdir(dirCtrl)
        if not os.path.isfile(dirCtrl+'/__init__.py'):
            initF = open(dirCtrl+'/__init__.py', "w")
            initF.close()
        if not os.path.isfile(jsonCtrl):
            x = []
            f = open(jsonCtrl, "w")
            json.dump(x, f)
            f.close()
        
        template = self.templateController.format(name)


        jsonF = open(jsonCtrl, "r+")
        ctrlList = json.load(jsonF)
        if name in ctrlList:
            return

        ctrlList.append(name)

        ctrlF = open(dirCtrl+'/'+name+'.py', "w")
        ctrlF.write(template)
        ctrlF.close()
        
        jsonF.seek(0)
        json.dump(ctrlList, jsonF, indent=2)
        jsonF.close()
        
        pass

    def generateMiddleware(self, name = None):
        dirCtrl = self.site+"/Middleware"
        jsonCtrl = dirCtrl+'/middleware.json'
        if not os.path.isdir(dirCtrl):
            os.mkdir(dirCtrl)
        if not os.path.isfile(dirCtrl+'/__init__.py'):
            initF = open(dirCtrl+'/__init__.py', "w")
            initF.close()
        if not os.path.isfile(jsonCtrl):
            x = []
            f = open(jsonCtrl, "w")
            json.dump(x, f)
            f.close()
        
        if name is None:
            return

    def generateDatabase(self, name = None):
        dirCtrl = self.site+"/Database"
        jsonCtrl = dirCtrl+'/database.json'
        if not os.path.isdir(dirCtrl):
            os.mkdir(dirCtrl)
        if not os.path.isfile(dirCtrl+'/__init__.py'):
            initF = open(dirCtrl+'/__init__.py', "w")
            initF.close()
        if not os.path.isfile(jsonCtrl):
            x = {}
            f = open(jsonCtrl, "w")
            json.dump(x, f)
            f.close()
        
        if name is None:
            return

    def generateModel(self, name = None):
        dirCtrl = self.site+"/Model"
        jsonCtrl = dirCtrl+'/model.json'
        if not os.path.isdir(dirCtrl):
            os.mkdir(dirCtrl)
        if not os.path.isfile(dirCtrl+'/__init__.py'):
            initF = open(dirCtrl+'/__init__.py', "w")
            initF.close()
        if not os.path.isfile(jsonCtrl):
            x = {}
            f = open(jsonCtrl, "w")
            json.dump(x, f)
            f.close()
        
        if name is None:
            return

    def generateService(self, name = None):
        dirCtrl = self.site+"/Service"
        jsonCtrl = dirCtrl+'/service.json'
        if not os.path.isdir(dirCtrl):
            os.mkdir(dirCtrl)
        if not os.path.isfile(dirCtrl+'/__init__.py'):
            initF = open(dirCtrl+'/__init__.py', "w")
            initF.close()
        if not os.path.isfile(jsonCtrl):
            x = {}
            f = open(jsonCtrl, "w")
            json.dump(x, f)
            f.close()
        
        if name is None:
            return

    def generateAuth(self, name = None):
        dirCtrl = self.site+"/Auth"
        jsonCtrl = dirCtrl+'/Auth.json'
        if not os.path.isdir(dirCtrl):
            os.mkdir(dirCtrl)
        if not os.path.isfile(dirCtrl+'/__init__.py'):
            initF = open(dirCtrl+'/__init__.py', "w")
            initF.close()
        if not os.path.isfile(jsonCtrl):
            x = {}
            f = open(jsonCtrl, "w")
            json.dump(x, f)
            f.close()
        
        if name is None:
            return

    def generateRoute(self, url, controller, prefix = None):
        dirCtrl = self.site+"/Route"
        jsonHtppPath = dirCtrl+'/http.json'
        jsonWsPath = dirCtrl+'/ws.json'
        if not os.path.isdir(dirCtrl):
            os.mkdir(dirCtrl)
        if not os.path.isfile(dirCtrl+'/__init__.py'):
            initF = open(dirCtrl+'/__init__.py', "w")
            initF.close()
        if not os.path.isfile(jsonHtppPath):
            x = []
            f = open(jsonHtppPath, "w")
            json.dump(x, f)
            f.close()
        if not os.path.isfile(jsonWsPath):
            x = []
            f = open(jsonWsPath, "w")
            json.dump(x, f)
            f.close()
        
        if url is None:
            return
        
        jsonHttpF = open(jsonHtppPath, "r+")
        httpList = json.load(jsonHttpF)
        router = self.getUrl(httpList, prefix)

        router.append(self.generateRouter(url, controller))
        
        jsonHttpF.seek(0)
        json.dump(httpList, jsonHttpF, indent=2)
        jsonHttpF.close()

    def getUrl(self, router: List, prefix) -> List:
        if prefix is None:
            return router
        else:
            return router

    def generateRouter(self, url, controller):
        # do validate here
        return {"url": url, "controller" : controller}

        

    templateConfig = "config={}"

    templateController = '''from Jati.Base.Controller import Controller
class {}(Controller):
    def index(self):
        return "Hello World"
'''