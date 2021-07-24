import socket
import base64
import struct
import json
import traceback
from hashlib import sha1
from ssl import SSLError
from typing import BinaryIO
from Jati.HTTPRequest import HTTPRequest
from Jati.HTTPResponse import HTTPResponse

class WebsocketClient:
    STATUS = {
        "SUCCESS" : 0x01,
        "SERVER_ERROR" : 0x81
    }
    def __init__(self):
        self.rfile: BinaryIO = None
        self.wfile: BinaryIO = None
        self.hostname = None
        self.protocol = ''
        self.message = [b'']
        self.closed = False
        self.session_id = None
        self.session = None
        self.events = {
            "close": []
        }
    
    #handsacking return response header
    def handsacking(self, request: HTTPRequest, response: HTTPResponse):
        # generate hash key from request key
        key = request.headers.get('Sec-WebSocket-Key', '')
        response.set_header('Sec-WebSocket-Accept', self.hash_key(key))

        protocol = request.headers.get('Sec-WebSocket-Protocol', None)
        version = request.headers.get('Sec-WebSocket-Version')
        
        response.set_header('Upgrade', "WebSocket")
        response.set_header('Connection', "Upgrade")
        response.set_header('Server', "Python-Websocket-Janoko")
        if protocol:
            response.set_header('Sec-WebSocket-Protocol', protocol)
        
        if protocol:
            self.protocol = protocol
        else:
            self.protocol = None
        
        request.connection.settimeout(1000)
        self.addr = request.client_address
        self.rfile = request.rfile
        self.wfile = request.wfile

    def hash_key(self, key):
        guid = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
        combined = (key + guid).encode('UTF-8')
        hashed = sha1(combined).digest()
        result = base64.b64encode(hashed).decode('UTF-8')
        return result
    
    def int_to_bytes(self, i):
        flag = 0
        b = b''
        if i < 126:
            flag |= i
            b += bytes([flag])

        elif i < (2 ** 16):
            flag |= 126
            b += bytes([flag])
            l = struct.pack(">H", i)
            b += l

        else:
            l = struct.pack(">Q", i)
            flag |= 127
            b += bytes([flag])
            b += l
        return b

    def decode_message(self, data):
        if len(self.message) != 3:
            self.message[0] += data
            data = self.message[0]
            lid = len(data)
            
            if data[0] == 136:
                self.close()
                return
            if lid < 6: # 1 + 1 + 4 (? + l_data + mask)
                return
            datalength = data[1] & 127
            mask_index = 2

            if datalength == 126:
                if lid < 8:
                    return
                mask_index = 4
                datalength = struct.unpack(">H", data[2:4])[0]
            elif datalength == 127:    
                if lid < 14:
                    return
                mask_index = 10
                datalength = struct.unpack(">Q", data[2:10])[0]
            self.message = [datalength, data[mask_index:mask_index+4], data[mask_index+4:]]
        else:
            self.message[2] += data
        
        if len(self.message[2]) < self.message[0]:
            return
        
        # Extract masks
        masks = self.message[1]
        msg = b''
        j = 0
        # Loop through each byte that was received
        for i in range(self.message[0]):
            # Unmask this byte and add to the decoded buffer
            msg += bytes([self.message[2][i] ^ masks[j]])
            j += 1
            if j == 4:
                j = 0
                
        self.on_message(msg.decode('UTF8'))
        if self.message[2][self.message[0]:] == b'':
            self.message = [b'']
        else:
            data = self.message[2][self.message[0]:]
            self.message = [b'']
            self.decode_message(data)

    def send_message(self, s, binary = False):
        """
        Encode and send a WebSocket message
        """
        # Empty message to start with
        message = b''
        # always send an entire message as one frame (fin)
        # default text
        b1 = 0x81

        if binary:
            b1 = 0x02
        
        # in Python 2, strs are bytes and unicodes are strings
        payload = s.encode("UTF8")

        # Append 'FIN' flag to the message
        message += bytes([b1])

        # How long is our payload?
        length = len(payload)
        message += self.int_to_bytes(length)

        # Append payload to message
        message += payload

        # Send to the client
        self.wfile.write(message)

    def send_respond(self, respMessage, status = 200, respData = None):
        resp = {
            "respond": respMessage,
            "status": status,
            "data": respData
        }
        
        self.send_message(json.dumps(resp))
        
    def on_new(self):
        pass

    def on_message(self, msg):
        pass

    def on_close(self):
        pass

    def on(self, event, _f):
        self.events[event].append(_f)

    def close(self):
        for _f in self.events["close"]:
            try:
                _f(self)
            except Exception:
                g = traceback.format_exc()
                # self.log.error(g)
        self.on_close()

    def handle(self):
        self.on_new()
        while not self.closed:
            try:
                data = self.rfile.read(2048)
                if not data:
                    self.close()
                    break
                self.decode_message(data)
                self.wfile.flush()
            except socket.timeout as e:
                # self.log.error("ws sock: %s", e)
                self.close()
                break
            except SSLError as e:
                # self.log.error("ws sock error ssl: %s", e)
                self.close()
                break
            except Exception as e:
                g = traceback.format_exc()
                # self.log.error(g)
                self.close_connection = 1
                break