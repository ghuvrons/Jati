import json, cgi
from urllib.parse import urlparse, parse_qs
from typing import BinaryIO, Tuple
from http.client import HTTPMessage

class HTTPRequest:
    def __init__(self):
        self.connection = None
        self.client_address: Tuple[str, int] = None
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

    def parsePath(self, path: str):
        url = urlparse(path)
        self.path = url.path
        self.query_parameters = parse_qs(url.query)


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