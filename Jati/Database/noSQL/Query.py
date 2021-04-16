from threading import Event

class QueryResult:
    def __init__(self, query, isSelectQuery = False):
        self.query = query
        self.event = Event()
        self.isSelectQuery = isSelectQuery
        self.cursor = None
        self.lastid = None
        self.error = None

    def __iter__(self):
        return self

    def __next__(self):
        if self.cursor is not None:
            data = self.cursor.fetchone()
            if data:
                return data
            self.cursor.close()
        raise StopIteration

class Query:
    QueryResult = QueryResult
    def __init__(self, collection, db = None):
        self.db = db
        self.collection = collection

    def insert(self, data): pass

    def update(self, data, where = None): pass

    def delete(self, where = None): pass

    def select(self, *column, **kwargs): pass

    def select_one(self, *column, **kwargs): pass

    def getResult(self): pass