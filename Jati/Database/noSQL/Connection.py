import threading

class Connection:
    def __init__(self, options):
        self.isBusy = False
        self.isLock = False
        self.db = None
        self.onAvailable = None
        self.onExpired = None
        self.listenerExec = threading.Event()
        self.isClosed = False
        default_db = {
            "host": "localhost",
            "port": 3306,
            "user": "root",
            "password": "",
            "database": "Jati"
        }
        self.options = default_db.copy()
        self.options.update({
            "transaction_only" : False
        })
        self.options.update(options)

    def execute(self, query): 
        try:
            cursor = self.db.cursor()
            cursor.execute(query.query)
            if query.isSelectQuery:
                query.cursor = cursor
            else:
                query.lastid = cursor.lastrowid
                cursor.close()
            self.db.commit()
        except Exception as e:
            if not query.isSelectQuery:
                self.db.rollback()
            query.error = e
        finally:
            query.event.set()
        if self.onAvailable:
            self.onAvailable(self)

    def close(self): pass
