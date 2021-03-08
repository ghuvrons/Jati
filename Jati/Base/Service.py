import threading, os, traceback

class Service(threading.Thread):
    STATUS_RUNNING = 0x80
    Databases = {}
    Models = {}
    Log = None

    def __init__(self):
        threading.Thread.__init__(self)
        self.listener = threading.Event()
        self.isClosed = False
        self.timeout = None
        self.tmpdata = None
        r, w = os.pipe()
        self.rpipe, self.wpipe = (os.fdopen(r, 'rb'), os.fdopen(w, 'wb'))
        self.clients = []
        self.__status =  0x00
    
    def addStreamer(self, req):
        if req.ws != None:
            self.clients.append(req.ws)
            def out(ws):
                self.clients.remove(ws)
            req.ws.on("close", out)

    def broadcast(self, resp, data):
        for c in self.clients:
            c.sendRespond(resp, respData = data)

    def run(self):
        while (self.listener.wait(self.timeout) or True) and not self.isClosed:
            try:
                if self.listener.is_set():
                    length = self.rpipe.read(1)[0]
                    if length == 0: break
                    event = self.rpipe.read(length).decode('UTF-8')
                    mname = 'on_' + event
                    if not hasattr(self, mname):
                        self.Log.error("Unsupported event (%r)" % event)
                    else:
                        method = getattr(self, mname)
                        method(self.tmpdata)
                    self.tmpdata = None
                else:
                    self.loop()
            except Exception:
                e = traceback.format_exc()
                self.Log.error(e)
            finally:
                self.listener.clear()
                self.__status ^= Service.STATUS_RUNNING
        self.wpipe.close()
        self.rpipe.close()

    def loop(self):
        pass

    def emit(self, event, data = None):
        if (self.__status & Service.STATUS_RUNNING == Service.STATUS_RUNNING): 
            return False
        self.__status |= Service.STATUS_RUNNING
        self.tmpdata = data
        self.writePipe(event)
        return True

    def writePipe(self, msg):
        l = len(msg)
        if l == 0: return
        if l > 255: return
        msg = bytes([l]) + msg.encode('UTF-8')
        self.wpipe.write(msg)
        self.wpipe.flush()
        self.listener.set()

    def close(self):
        self.isClosed = True
        self.listener.set()