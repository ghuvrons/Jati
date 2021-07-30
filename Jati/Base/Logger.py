import logging, os, sys
from logging.handlers import TimedRotatingFileHandler
FORMATTER = logging.Formatter("%(asctime)s [%(levelname)s]: %(message)s")


def get_console_handler():
    """Get STDOUT from system for handle log"""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(FORMATTER)
    return handler


def get_file_handler(filepath):
    """Get file for handle log"""
    handler = TimedRotatingFileHandler(filepath, when='midnight')
    handler.setFormatter(FORMATTER)
    return handler


class Logger:
    """
    Base Logger
    """

    def __init__(self, name = 'Jati', filepath = None):
        self.isTmpFull = False
        self.tmp = []
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
            
    def debug(self, msg, *args): self.logger.debug(msg, *args)
    def info(self, msg, *args): self.logger.info(msg, *args)
    def warning(self, msg, *args): self.logger.warning(msg, *args)
    def error(self, msg, *args): self.logger.error(msg, *args)