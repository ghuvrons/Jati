import os, json

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

    templateConfig = "config={}"

    templateController = '''from Jati.Base.Controller import Controller
class {}(Controller):
    def index(self, req, session):
        return "Hello World"
'''