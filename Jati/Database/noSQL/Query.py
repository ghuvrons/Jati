from threading import Event

class QueryResult:
    def __init__(self, cursor):
        self.cursor = cursor
        self.error = None

    def limit(n):
        self.cursor = self.cursor.limit(n)

    def __iter__(self):
        return self

    def __next__(self):
        if self.cursor is not None:
            data = self.cursor.__next__()
            if data:
                return data
        raise StopIteration

class Query:
    QueryResult = QueryResult
    def __init__(self, collection, db = None):
        self.db = db
        self.collection = collection

    def insert(self, data): pass

    def update(self, data, where = None): pass

    def delete(self, where = None): pass

    def select(self, where = None): pass

    def select_one(self, where = None): pass