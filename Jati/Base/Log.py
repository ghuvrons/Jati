import logging, os, sys, datetime
from logging.handlers import TimedRotatingFileHandler
FORMATTER = logging.Formatter("%(asctime)s [%(levelname)s]: %(message)s")

def get_console_handler():
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(FORMATTER)
    return handler

def get_file_handler(filepath):
    handler = TimedRotatingFileHandler(filepath, when='midnight')
    handler.setFormatter(FORMATTER)
    return handler

class Log:
    def __init__(self, name = 'Jati', filepath = None):
        self.isTmpFull = False
        self.tmp = []
        self.streamer = None
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        if filepath == None:
            self.logger.addHandler(get_console_handler())
        else:
            dirname = os.path.dirname(filepath)
            if not os.path.isdir(dirname):
                os.mkdir(dirname)
            self.logger.addHandler(get_file_handler(filepath))
        self.logger.propagate = False
    
    def write(self, log):
        tmp = (datetime.datetime.now(), '{}'.format(log))
        if self.streamer:
            try:
                date, log = tmp
                self.streamer.send('\n'+date.strftime("%c")+'\n'+str(log))
            except:
                self.streamer = None
        self.tmp.append(tmp)
        if len(self.tmp) > 100:
            self.tmp.pop(0)
            
    def debug(self, msg, *args): self.logger.debug(msg, *args)
    def info(self, msg, *args): self.logger.info(msg, *args)
    def warning(self, msg, *args): self.logger.warning(msg, *args)
    def error(self, msg, *args): self.logger.error(msg, *args)
    
    def addStreamer(self, sock):
        for tmp in self.tmp:
            date, log = tmp
            sock.send(date.strftime("%c")+'\n'+str(log))
        self.streamer = sock