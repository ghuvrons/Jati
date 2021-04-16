import _thread
import time
from .Connection import Connection
from .Query import Query

class Database:
    Q = Query

    def __init__(self, options, dbs_read = []):
        self.availableConnection = []
        self.allConnection = []
        self.queue = []
        self.maxConn = 1
        self.options = options

    def onAvailableConnection(self, conn):
        self.availableConnection.append(conn)
        self.shiftQueue()

    def onExpiredConnection(self, conn):
        try:
            self.allConnection.remove(conn)
            self.availableConnection.remove(conn)
        except:
            pass
        
    ##
    #
    # 1. dicari conn yang available
    # 2. jika g ada bikin conn lagi.
    # 3. jika melebihi maxConn. maka nunggu available
    def shiftQueue(self):
        try:
            if len(self.queue) == 0: return
            conn = None
            if len(self.availableConnection) > 0:
                conn = self.availableConnection.pop()
            elif len(self.allConnection) < self.maxConn:
                newConnection = self.createConnection()
                newConnection.onAvailable = self.onAvailableConnection
                newConnection.onExpired = self.onExpiredConnection
                self.allConnection.append(newConnection)
                conn = newConnection

            if conn is not None and len(self.queue) > 0:
                query = self.queue.pop(0)
                _thread.start_new_thread( conn.execute, (query, ) )

        except IndexError:
            pass
    
    def addQueue(self, query):
        self.queue.append(query)
        self.shiftQueue()

    def execute(self, query):
        if type(query) is str:
            queryResult = self.Query.QueryResult(query)
        else:
            queryResult = query.QueryResult(query.query, query.isSelectQuery)
        queryResult.event.clear()
        self.addQueue(queryResult)
        if queryResult.event.wait(30):
            if queryResult.error:
                raise queryResult.error
            return queryResult
        else:
            self.queue.remove(queryResult)

    def createConnection(self):
        return Connection(self.options)

    def __getitem__(self, table):
        return Query(table, self)

    def close(self):
        for conn in self.allConnection:
            conn.close()
