import traceback
import socket
import mimetypes
import os, ssl, json, decimal
from http.server import BaseHTTPRequestHandler, HTTPStatus

from .Error import JatiError
from .HTTPResponse import HTTPResponse
from .HTTPRequest import HTTPRequest
from .Base.App import App as BaseApp
from .Base.Session import Session

def encode_complex(obj): 
    if isinstance(obj, complex): 
        return [obj.real, obj.imag] 
    elif isinstance(obj, decimal.Decimal):
        return float(obj)
    elif '__dict__' in dir(obj):
        return obj.__dict__
    raise TypeError(repr(obj) + " is not JSON serializable.") 

class HTTPClientHandler(BaseHTTPRequestHandler):
    isSSL = False

    def __init__(self, connection, server_socket, client_address, Applications, close_listener = None):
        self.Applications = Applications
        connection.settimeout(100) 
        self.hostname = None
        self.client_sock = connection
        self.client_address = client_address
        self.isSetupSuccess = True

        self._request = HTTPRequest()
        self._request.client_address = client_address
        self._response = HTTPResponse()
        self._session: Session = None

        if close_listener != None: self.on_closing = close_listener
        BaseHTTPRequestHandler.__init__(self, connection, client_address, server_socket)

    def servername_callback(self, sock, req_hostname, cb_context, as_callback=True):
        self.hostname = req_hostname
        try:
            app = self.Applications.get(req_hostname, self.Applications['localhost'])
            sock.context = app.ssl_context
        except Exception:
            g = traceback.format_exc()
            self.log_error("ssl error %s", g)
        
    def setup(self):
        try:
            if HTTPClientHandler.isSSL:
                context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
                context.set_servername_callback(self.servername_callback)
                context.load_cert_chain(certfile="/etc/ssl/certs/ssl-cert-snakeoil.pem",
                                        keyfile="/etc/ssl/private/ssl-cert-snakeoil.key")
                self.request = context.wrap_socket(
                    self.request, 
                    server_side=True
                )
        except Exception:
            g = traceback.format_exc()
            self.log_error("ssl error %s", g)
            self.isSetupSuccess = False
        BaseHTTPRequestHandler.setup(self)

    def set_app(self, jatiApp: BaseApp): pass

    def on_new_request(self):
        self._request.connection = self.client_sock
        self._request.rfile = self.rfile
        self._request.wfile = self.wfile
        self._request.headers = self.headers
        self._request.parsePath(self.path)

        Apps = self.Applications
        if self.hostname == None:
            host = self.headers.get("Host", "").split(":")[0]
            if host != '':
                self.hostname = host

        jatiApp: BaseApp = Apps[self.hostname] if self.hostname in Apps else Apps["localhost"]
        self.set_app(jatiApp)

        cookies = jatiApp.Session.get_cookies(self)
        if self._session and ("PySessID" in cookies and self._session.id != cookies["PySessID"]):
            self._session = None

    def do_GET(self):
        self.handle_request('get')

    def do_POST(self):
        self.handle_request('post')
    
    def handle_request(methos: str): pass

    def handle_one_request(self):
        try:
            self.raw_requestline = self.rfile.readline(65537)
            if not self.isSetupSuccess:
                self.requestline = ''
                self.request_version = ''
                self.command = ''
                self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR)
                self.close_connection = True
                return
            if len(self.raw_requestline) > 65536:
                self.requestline = ''
                self.request_version = ''
                self.command = ''
                self.send_error(HTTPStatus.REQUEST_URI_TOO_LONG)
                return
            if not self.raw_requestline:
                self.close_connection = True
                return
            if not self.parse_request():
                # An error code has been sent, just exit
                return
            mname = 'do_' + self.command
            if not hasattr(self, mname):
                self.send_error(
                    HTTPStatus.NOT_IMPLEMENTED,
                    "Unsupported method (%r)" % self.command)
                return
                
            self.on_new_request()
            method = getattr(self, mname, None)
            if method: method()

            #actually send the response if not already done.
            self.wfile.flush()
            self._request.flush()
            self._response.flush()

        except socket.timeout as e:
            #a read or a write timed out.  Discard this connection
            self.log_error("Request timed out: %r", e)
            self.close_connection = True
            return

    def send_response_message(self, code, msg = '', header_message = None):
        self.send_response(code, header_message)
        msg_attr = dir(msg)
        if 'name' in msg_attr and 'fileno' in msg_attr:
            self.send_header("Content-Length", os.fstat(msg.fileno()).st_size)
            ext = msg.name.split('.')[-1]
            if ext in self.contentType:
                self.send_header("Content-Type", self.contentType[ext])
            else:
                ext_type = mimetypes.guess_type(msg.name)[0]
                if ext_type and ext_type.split('/')[0] == 'text':
                    self.send_header("Content-Type", 'text/plain')
                else:
                    self.send_header("Content-Type", 'application/octet-stream')
            if self._response.headers.get('Content-Type', False):
                del self._response.headers['Content-Type']
        elif self._response.headers.get('Content-Type') == "application/json":
            msg = json.dumps(msg, default=encode_complex)
            self.send_header("Content-Length", len(msg))
        elif type(msg) == str:
            self.send_header("Content-Length", len(msg))
        else:
            msg = '{}'.format(msg)
            self.send_header("Content-Length", len(msg))
        for key in self._response.headers.keys():
            self.send_header(key, self._response.headers[key])
        self.end_headers()
        
        if 'name' in msg_attr and 'fileno' in msg_attr:
            while True:
                s = msg.read()
                if s: self.connection.send(s)
                else: break
            msg.close()
        else:
            if msg != '':
                self.connection.send(msg.encode('utf-8'))

    def on_closing(self, connection): pass

    def close(self):
        self.on_closing(self.connection)
        self.close_connection = True

    def __del__(self):
        self.log_message("client remove - %r", self.client_address)

    contentType = {
        'aac': 'audio/aac',
        'abw': 'application/x-abiword',
        'arc': 'application/x-freearc',
        'avi': 'video/x-msvideo',
        'azw': 'application/vnd.amazon.ebook',
        'bin': 'application/octet-stream',
        'bmp': 'image/bmp',
        'bz': 'application/x-bzip',
        'bz2': 'application/x-bzip2',
        'csh': 'pplication/x-csh',
        'css': 'text/css',
        'csv': 'text/csv',
        'doc': 'application/msword',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'eot': 'application/vnd.ms-fontobject',
        'epub': 'application/epub+zip',
        'gz': 'application/gzip',
        'gif': 'image/gif',
        'htm' :'text/html',
        'html': 'text/html',
        'ico': 'image/vnd.microsoft.icon',
        'ics': 'text/calendar',
        'jar': 'application/java-archive',
        'jpeg': 'image/jpeg',
        'jpg': 'image/jpeg',
        'js': 'text/javascript',
        'json': 'application/json',
        'jsonld': 'application/ld+json',
        'mid': 'audio/midi audio/x-midi',
        'midi': 'audio/midi audio/x-midi',
        'mjs': 'text/javascript',
        'mp3': 'audio/mpeg',
        'mp4 ': 'video/mpeg',
        'mpeg ': 'video/mpeg',
        'mpkg': 'application/vnd.apple.installer+xml',
        'odp': 'application/vnd.oasis.opendocument.presentation',
        'ods': 'application/vnd.oasis.opendocument.spreadsheet',
        'odt': 'application/vnd.oasis.opendocument.text',
        'oga': 'audio/ogg',
        'ogv': 'video/ogg',
        'ogx': 'application/ogg',
        'opus': 'audio/opus',
        'otf': 'font/otf',
        'png': 'image/png',
        'pdf': 'application/pdf',
        'php': 'application/php',
        'ppt': 'application/vnd.ms-powerpoint',
        'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'rar': 'application/x-rar-compressed',
        'rtf': 'application/rtf',
        'sh': 'pplication/x-sh',
        'svg': 'image/svg+xml',
        'swf': 'application/x-shockwave-flash',
        'tar': 'application/x-tar',
        'tif': 'image/tiff',
        'tiff': 'image/tiff',
        'ts': 'video/mp2t',
        'ttf': 'font/ttf',
        'txt': 'text/plain',
        'vsd': 'application/vnd.visio',
        'wav': 'audio/wav',
        'weba': 'audio/webm',
        'webm': 'video/webm',
        'webp': 'image/webp',
        'woff': 'font/woff',
        'woff2': 'font/woff2',
        'xhtml': 'application/xhtml+xml',
        'xls': 'application/vnd.ms-excel',
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'xml': 'application/xml',
        'xul': 'application/vnd.mozilla.xul+xml',
        'zip': 'application/zip',
        '3gp': 'video/3gpp',
        '3g2': 'video/3gpp2',
        '7z': 'application/x-7z-compressed'
    }