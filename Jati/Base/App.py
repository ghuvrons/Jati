from .Logger import Logger
from .Session import SessionHandler
from .Route import Router, BaseRoute, json_to_router
from .Auth import AuthHandler
import sys, json, ssl

class App:
    """
    App class will handle host site
    """

    def __init__(self, app_module, config = {}):    
        self.app_module = app_module
        self.appPath = app_module.__path__[0]
        self.Databases = {}
        self.Models = {}
        self.Modules = {}
        self.Services = {}
        self.router: Router = None
        self.Log = Logger('Jati.'+app_module.__name__, filepath=self.appPath+"/Log/log.log")
        self.authHandler = AuthHandler()
        self.load_app_system()

        self.default_config = {
            "Session-path" : self.appPath+"/session.pkl",
            "limit": {
                "upload": 10000000, #10MB
            }
        }
        self.default_config.update(config)
        self.config = self.default_config

        if 'SSL' in self.config:
            self.ssl_context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH, cafile=self.config["SSL"]["ca_certs"])
            self.ssl_context.load_cert_chain(
                certfile=self.config["SSL"]["certfile"],
                keyfile=self.config["SSL"]["keyfile"]
            )

        self.Session = SessionHandler(self.config["Session-path"])
        self.Session.start()


    def load_app_system(self):
        """
        Load all requrement from application module.
        """
        app_mod_name = self.app_module.__name__
        __import__(app_mod_name, fromlist=[
            "Controller", "Middleware", "Database", "Service", "Model", "Route"
        ])

        # Load Controllers module
        # Controllers class will be save in route. see Jati.Base.Route
        try:
            controller_json = open(sys.modules[app_mod_name+".Controller"].__path__[0]+"/controller.json")
            controller_list = json.load(controller_json)
            controller_json.close()
            __import__(app_mod_name+".Controller", fromlist=[str(s) for s in controller_list], globals=globals())
        except Exception as e:
            self.Log.error( "Controller error : %s", e)
            pass

        # Load Middlewares
        # as controllers. Middleware class will be save in route. see Jati.Base.Route
        try:
            middleware_json = open(sys.modules[app_mod_name+".Middleware"].__path__[0]+"/middleware.json")
            middleware_list = json.load(middleware_json)
            middleware_json.close()
            __import__(app_mod_name+".Middleware", fromlist=[str(s) for s in middleware_list], globals=globals())
        except Exception as e:
            self.Log.error( "Middleware error : %s", e)
            pass

        # Load Database Driver
        try:
            database_json = open(sys.modules[app_mod_name+".Database"].__path__[0]+"/database.json")
            database_obj = json.load(database_json)
            database_json.close()

            for db_key in database_obj.keys():
                db_config = database_obj[db_key]
                __import__(db_config['driver'])
                self.Databases[db_key] = sys.modules[db_config['driver']].db(db_config['config'])
        except Exception as e:
            self.Log.error( "Database error : %s", e)
            pass

        # Load Model
        try:
            model_json = open(sys.modules[app_mod_name+".Model"].__path__[0]+"/model.json")
            model_obj = json.load(model_json)
            model_json.close()

            for sr_key in model_obj.keys():
                model_class_name = model_obj[sr_key].split(".")
                tmp_model_mod = app_mod_name+".Model"
                for model_mod_name in model_class_name[:-1]:
                    __import__(tmp_model_mod, fromlist=[str(model_mod_name)])
                    tmp_model_mod += "."+str(model_mod_name)
                model_class = getattr(sys.modules[tmp_model_mod], str(model_class_name[-1]))
                self.Models[sr_key] = model_class
                self.Models[sr_key].Databases = self.Databases
                self.Models[sr_key].Services = self.Services
                self.Models[sr_key].Log = self.Log
        except Exception as e:
            self.Log.error("Model error : %s", e)
            pass
        
        # Load Service instance
        try:
            service_json = open(sys.modules[app_mod_name+".Service"].__path__[0]+"/service.json")
            service_obj = json.load(service_json)
            service_json.close()

            for sr_key in service_obj.keys():
                service_class_name = service_obj[sr_key].split(".")
                tmp_service_mod = app_mod_name+".Service"
                for service_mod_name in service_class_name[:-1]:
                    __import__(tmp_service_mod, fromlist=[str(service_mod_name)])
                    tmp_service_mod += "."+str(service_mod_name)
                service_class = getattr(sys.modules[tmp_service_mod], str(service_class_name[-1]))
                service_class.Databases = self.Databases
                service_class.Models = self.Models
                service_class.Log = self.Log
                self.Services[sr_key] = service_class()
                self.Services[sr_key].start()
        except Exception as e:
            self.Log.error( "Service error : %s", e)
            pass

        # Load Router
        try:
            route_config = json_to_router(sys.modules[app_mod_name+".Route"].__path__[0]+"/http.json")

            route = BaseRoute(self.app_module)
            route.Log = self.Log
            route.Databases = self.Databases
            route.Models = self.Models
            route.Modules = self.Modules
            route.Services = self.Services
            route.generate_route(route_config)

            self.router = route.router

            # httpRouter.print()

        except Exception as e:
            self.Log.error("Route error : %s", e)
            pass

        # Load Authenticator
        try:
            auth_config_json = open(sys.modules[app_mod_name].__path__[0]+"/Auth/Auth.json")
            auth_config = json.load(auth_config_json)
            auth_config_json.close()
            self.authHandler.setUserModel(self.Models[auth_config['user']])
            
            auth_key_file = open(sys.modules[app_mod_name].__path__[0]+"/Auth/auth.key")
            auth_key = auth_key_file.read()
            auth_key_file.close()
            self.authHandler.setSecretKey(auth_key)
        except Exception as e:
            self.Log.error("Auth error : %s", e)
            pass


    def print_all_modules(self):
        modules = sys.modules.keys()
        modules.sort()
        for m in modules:
            print(m)


    def close(self):
        """Close application"""

        self.Session.close()
        if 'Module' in dir(self.app_module) and hasattr(self.app_module.Module, 'close'):
            self.app_module.Module.close()
        if hasattr(self.app_module.Database, 'close'):
            self.app_module.Database.close()
        
        for k in self.Services.keys():
            self.Services[k].close()