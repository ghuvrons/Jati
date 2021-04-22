import _thread
import time
from .Connection import Connection
from .Query import Query

class Database:
    Q = Query
    def __init__(self, options, dbs_read = []):
        self.options = options
        self.connection = self.createConnection()

    def createConnection(self):
        return Connection(self.options)

    def __getitem__(self, collection):
        return self.Q(collection, self)

    def close(self):
        pass
