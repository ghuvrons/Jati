import json, cgi
from typing import BinaryIO
from http.client import HTTPMessage

from .Error import WSError

class HTTPRequest:
    def __init__(self):
        self.connection = None
        self.client_address: tuple = None
        self.rfile: BinaryIO = None
        self.wfile: BinaryIO = None
        self.headers: HTTPMessage = None
        self.path: str = None
        self.parameters = {}
        self.query_parameters = {}
        self.data = None

    def flush(self):
        self.parameters = {}
        self.query_parameters = {}
        self.data = None

    def setHeader(self, headers: HTTPMessage):
        self.headers = headers

    def parseData(self):
        if self.headers is None: return
        if not 'Content-Type' in self.headers:
            self.data = None
        elif self.headers['Content-Type'] == "application/json":
            self.data = json.loads(self.rfile.read(int(self.headers['Content-Length'])).decode('UTF-8'))
        else:
            self.data = cgi.FieldStorage(
                    fp=self.rfile, 
                    headers=self.headers,
                    environ={'REQUEST_METHOD':'POST',
                                'CONTENT_TYPE':self.headers['Content-Type']
                    })
    
    def parseWsData(self, msg):
        try:
            msg = json.loads(msg)
            # msg = {
            #     'request': ...
            #     'data': ...
            # }
        except ValueError:
            return
        
        if not 'request' in msg:
            raise WSError(500)
        request = str(msg["request"])
        if not 'data' in msg:
            msg["data"] = {}
        self.data = msg["data"]

        return request
