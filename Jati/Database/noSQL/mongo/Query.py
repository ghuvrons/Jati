class Query:
    QueryResult = QueryResult
    def __init__(self, collection, db = None):
        self.db = db
        self.collection = collection

    def insert(self, data): 
        return self.db.connection[self.collection].insert_one(data).inserted_id

    def update(self, data, where): 
        return self.db.connection[self.collection].update_many(where, data).inserted_id

    def delete(self, where): 
        return self.db.connection[self.collection].delete_many(where).inserted_id

    def select(self, where):
        return self.QueryResult(self.db.connection[self.collection].find(where))

    def select_one(self, where): 
        return self.db.connection[self.collection].find_one(where)
