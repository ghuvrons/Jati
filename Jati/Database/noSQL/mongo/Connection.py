from ..Connection import Connection as BaseConnection
import pymongo

class Connection(BaseConnection):
    def __init__(self, options):
        BaseConnection.__init__(self, options)
        self.db = pymongo.MongoClient("localhost", 27017)
        
    def close():
        self.db.close()
