import os, json, traceback
from inspect import getfullargspec
from .Error import *
from .Base.App import App as JatiApp
from .HTTPClientHandler import HTTPClientHandler
from .HTTPRequest import HTTPRequest
from .HTTPResponse import HTTPResponse
from .WebsocketClient import WebsocketClient

class Client(HTTPClientHandler):
    def __init__(self, connection, client_address, Applications, server):
        if not Applications:
            raise JatiError("Application module is not set yet.")
        self.app: JatiApp = None
        self.session = None
        self.auth = None
        server.client_create_listener(self)
        super().__init__(
            connection, 
            server.server_socket, 
            client_address, 
            Applications, 
            server.client_close_listener
        )

    def set_app(self, app: JatiApp):
        self.app = app

    def run_authorization(self):
        auth_token = self._request.headers.get("Authorization", None)
        if auth_token:
            auth_type, auth_token = auth_token.split(" ", 1)
            self.auth = self.app.authHandler.authenticate(auth_type, auth_token, auth=self.auth)

    def run_middleWare(self, method, middlewares):
        middleware_has_run = []
        for middleware in middlewares:
            if getfullargspec(middleware).varkw is None:
                if not middleware():
                    raise HTTPError(400)
            else:
                kw = {
                    "request": self._request,
                    "response": self._response,
                    "session": None,
                    "auth": self.auth
                }
                if not middleware(**kw):
                    raise HTTPError(400)

    def run_controller(self, controller):
        if getfullargspec(controller).varkw is None:
            response_message = controller()
        else:
            kw = {
                "request": self._request,
                "response": self._response,
                "session": None,
                "auth": self.auth
            }
            response_message = controller(**kw)
        return response_message
    
    def handle_error(self, errorHandler, status, message, e, traceback_e = None):
        if getfullargspec(errorHandler).varkw is None:
            response_message = errorHandler()
        else:
            kw = {
                "request": self._request,
                "response": self._response,
                "session": None,
                "auth": self.auth,
                "error": e,
                "error_code": status,
                "error_message": message,
                "traceback": traceback_e,
            }
            response_message = errorHandler(**kw)
        return response_message
        
    def handle_request(self, method: str):
        errorHandler = None
        if method == 'post':
            self._request.parseData()
        elif method == 'get':
            if os.path.exists(self.app.appPath+'/Public'+self._request.path):
                path = (self.app.appPath+'/Public'+self._request.path).replace('/../', '/')
                if os.path.isdir(path):
                    path += 'index.html'
                if os.path.isfile(path):
                    f = open(path, 'rb')
                    self.send_response_message(200, f)
                    return
        try:
            origin = self._request.headers.get("Origin")
            try:
                if origin in self.app.config["Access-Control-Allow"]["Origins"] or '*' in self.app.config["Access-Control-Allow"]["Origins"]:
                    self._response.set_header('Access-Control-Allow-Origin', origin)
            except:
                pass
            try:
                if self.app.config["Access-Control-Allow"]["Credentials"]:
                    self._response.set_header('Access-Control-Allow-Credentials', "true")
            except:
                pass

            self.run_authorization()
            middleware, controller, self.parameter, errorHandler = self.app.route['http'].search(self._request.path, method)
            self.run_middleWare(method, middleware)

            # upgrade protocol
            if 'Sec-WebSocket-Key' in self._request.headers:
                ws = WebsocketClient(self)
                self.session = self.app.Session.create(self)
                ws.handsacking(self._request, self._response)
                self.send_response_message(101, header_message = "Switching Protocols")
                ws.on_close = self.close
                ws.handle()
                return
            self.data = None

            if not controller:
                raise HTTPError(404, "Not found")
            response_message = ""
            response_message = self.run_controller(controller)
            self.send_response_message(200, response_message)

        except HTTPError as e:
            if errorHandler is not None:
                try:
                    self.send_response_message(
                        e.args[0], 
                        self.handle_error(errorHandler, e.args[0], e.args[1] if len(e.args) > 1 else None, e)
                    )
                except Exception as e:
                    traceback_e = traceback.format_exc()
                    self.app.Log.error(traceback_e)
                    self.send_response_message(500, "Error Handler error. Please, see log.")
            else:
                self.send_response_message(e.args[0], e.args[1])

        except Exception as e:
            traceback_e = traceback.format_exc()
            self.app.Log.error(traceback_e)
            if errorHandler is not None:
                try:
                    self.send_response_message(
                        500, 
                        self.handle_error(errorHandler, 500, "Internal server error", e, traceback_e)
                    )
                except Exception as e:
                    traceback_e = traceback.format_exc()
                    self.app.Log.error(traceback_e)
                    self.send_response_message(500, "Error Handler error. Please, see log.")
            else:
                self.send_response_message(500, "Internal server error")