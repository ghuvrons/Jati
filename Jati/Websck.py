import socket
import base64
import struct
import time
import random
import json
import os, select
import traceback
from hashlib import sha1
from ssl import SSLError

class ClientHandler():
    STATUS = {
        "SUCCESS" : 0x01,
        "SERVER_ERROR" : 0x81
    }
    def __init__(self, HTTPReqHandler):
        self.HTTPReqHandler = HTTPReqHandler
        self.addr = HTTPReqHandler.client_address
        self.hostname = None
        self.protocol = ''
        self.message = [b'']
        self.closed = False
        self.session_id = None
        self.session = None
        self.log = self.HTTPReqHandler.app.Log
        self.events = {
            "close": []
        }
    #handsacking return protocol
    def handsacking(self):
        origin = self.HTTPReqHandler.headers.get("Origin")
        try:
            if origin in self.HTTPReqHandler.app.config["Access-Control-Allow"]["Origins"]:
                self.HTTPReqHandler.set_respone_header('Access-Control-Allow-Origin', origin)
        except:
            pass
        try:
            if self.HTTPReqHandler.app.config["Access-Control-Allow"]["Credentials"]:
                self.HTTPReqHandler.set_respone_header('Access-Control-Allow-Credentials', "true")
        except:
            pass
        
        key = self.HTTPReqHandler.headers.get('Sec-WebSocket-Key', '')
        acc = self.hashKey(key)
        protocol = self.HTTPReqHandler.headers.get('Sec-WebSocket-Protocol')
        version = self.HTTPReqHandler.headers.get('Sec-WebSocket-Version')
        
        self.HTTPReqHandler.set_respone_header('Upgrade', "WebSocket")
        self.HTTPReqHandler.set_respone_header('Connection', "Upgrade")
        
        self.HTTPReqHandler.set_respone_header('Sec-WebSocket-Accept', acc)
        if protocol:
            self.HTTPReqHandler.set_respone_header('Sec-WebSocket-Protocol', protocol)
        self.HTTPReqHandler.set_respone_header('Server', "Python-Websocket-Janoko")
        
        self.HTTPReqHandler.send_response_message(101, header_message = "Switching Protocols")
        if protocol:
            self.protocol = protocol
        else:
            self.protocol = None
        return True

    def hashKey(self, key):
        guid = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
        combined = (key + guid).encode('UTF-8')
        hashed = sha1(combined).digest()
        result = base64.b64encode(hashed).decode('UTF-8')
        return result
    
    def intToBytes(self, i):
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

    def decodeMessage(self, data):
        if len(self.message) != 3:
            self.message[0] += data
            data = self.message[0]
            lid = len(data)
            
            if data[0] == 136:
                self.HTTPReqHandler.close()
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
                
        self.onMessage(msg.decode('UTF8'))
        if self.message[2][self.message[0]:] == b'':
            self.message = [b'']
        else:
            data = self.message[2][self.message[0]:]
            self.message = [b'']
            self.decodeMessage(data)

    def sendMessage(self, s, binary = False):
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
        message += self.intToBytes(length)

        # Append payload to message
        message += payload

        # Send to the client
        self.HTTPReqHandler.connection.send(message)

    def sendRespond(self, respMessage, status = 200, respData = None):
        resp = {
            "respond": respMessage,
            "status": status,
            "data": respData
        }
        
        self.sendMessage(json.dumps(resp))
        
    def onNew(self):
        pass

    def onMessage(self, msg):
        pass

    def on(self, event, _f):
        self.events[event].append(_f)

    def close(self):
        for _f in self.events["close"]:
            try:
                _f(self)
            except Exception:
                g = traceback.format_exc()
                self.log.error(g)
        self.HTTPReqHandler.close()

    def handle(self):
        if self.handsacking():
            self.onNew()
            self.HTTPReqHandler.connection.settimeout(1000)
            while not self.closed:
                try:
                    data = self.HTTPReqHandler.connection.recv(2048)
                    if not data:
                        self.close()
                        break
                    self.decodeMessage(data)
                    self.HTTPReqHandler.wfile.flush()
                except socket.timeout as e:
                    self.log.error("ws sock: %s", e)
                    self.close()
                    break
                except SSLError as e:
                    self.log.error("ws sock error ssl: %s", e)
                    self.close()
                    break
                except Exception as e:
                    g = traceback.format_exc()
                    self.log.error(g)
                    self.close_connection = 1
                    break