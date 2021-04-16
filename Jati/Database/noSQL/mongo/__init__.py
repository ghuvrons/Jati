from .Connection import Connection
from .Query import Query
from ..Database import Database

class db(Database):
    Q = Query

    def createConnection(self):
        return Connection(self.options)