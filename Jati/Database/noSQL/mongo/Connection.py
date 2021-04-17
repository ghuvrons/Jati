from ..Connection import Connection as BaseConnection
import pymongo

class Connection(BaseConnection):
    def __init__(self, options):
        BaseConnection.__init__(self, options)
        self.db = getattr(pymongo.MongoClient("localhost", 27017), options['database'])
        
    def close():
        self.db.close()

    def __getitem__(self, collection):
        return getattr(self.db, collection)
