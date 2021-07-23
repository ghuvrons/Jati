from http.server import HTTPServer
from socketserver import ThreadingTCPServer
from .Client import Client

class Server(HTTPServer, ThreadingTCPServer):
    def __init__(self, host: str, port: int, RequestHandlerClass: Client):
        HTTPServer.__init__(self, (host, port), RequestHandlerClass)
        self.applications = None
        self.server_socket = None
        self.clients = []

    def finish_request(self, request, client_address):
        """Finish one request by instantiating RequestHandlerClass."""
        client = self.RequestHandlerClass(request, client_address, self.applications, self)
        self.clients.remove(client)
    
    def client_create_listener(self, client: Client):
        self.clients.append(client)
        
    def client_close_listener(self, client_socket):
        self.shutdown_request(client_socket)