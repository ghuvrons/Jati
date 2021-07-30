import traceback, sys, os, json
from .Base.AppManager import AppManager
from .Base.App import App as BaseApp
from .Base.Logger import Logger
from .Server import Server
from .Client import Client

class Jati:
    def __init__(self, host = "127.0.0.1", port=3000, isSSL = False, log_file = None):
        self.applications = AppManager()
        self.server = None
        self.host = host
        self.port = port
        self.isSSL = isSSL
        main_module = sys.modules["__main__"]
        self.main_path = os.path.dirname(os.path.abspath(main_module.__file__))
        self.log_file = log_file
        self.log = Logger('Jati', filepath=log_file)


    def start(self):
        # self.setting = SettingHandler(self.main_path+"/setting.sock")
        # self.setting.cmd = self.cmd
        # self.setting.start()

        start_message = '''
Jati start on:
Host : {host}
Port : {port}
Mode : -
Log File : {log}
        '''
        print(start_message.format(host = self.host, port = self.port, log = self.log_file))

        Client.protocol_version = 'HTTP/1.1'
        Client.isSSL = self.isSSL
        Client.log_message = self.log_info
        Client.log_error = self.log_error
        self.server = Server(self.host, self.port, Client)
        self.server.applications = self.applications
        self.server.serve_forever()


    def addVHost(self, vhosts):
        for vh in vhosts:
            _project = vhosts[vh]
            self.applications.create_app(vh, _project)


    def log_info(self, msg, *args):
        self.log.info(msg, *args)


    def log_error(self, msg, *args):
        self.log.error(msg, *args)


    def close(self):
        for c in self.server.clients:
            c.close()
        # self.setting.close()
        self.server.server_close()
        self.applications.close()
