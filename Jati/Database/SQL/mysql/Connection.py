from ..Connection import Connection as BaseConnection
import pymysql

class Connection(BaseConnection):
    def __init__(self, options):
        BaseConnection.__init__(self, options)
        self.db = pymysql.connect(
            host=self.options['host'],
            user=self.options['user'],
            password=self.options['password'],
            database=self.options['database'],
            port=self.options['port'],
            cursorclass=pymysql.cursors.DictCursor
        )
    def close():
        self.db.close()
