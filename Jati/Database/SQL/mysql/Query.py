from threading import Event
import datetime
from ..Query import Query as baseQuery

class Query(baseQuery):
    def getResult(self):
        if self.result.result is not None:
            return self.result
        if self.isSelectQuery:
            return self.db.execute(self)
