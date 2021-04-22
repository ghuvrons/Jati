from threading import Event
import datetime
from ..Query import Query as baseQuery

class Query(baseQuery):
    def getResult(self):
        return self.db.execute(self)
