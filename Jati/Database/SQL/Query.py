from threading import Event
import datetime

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
    operator = ["=", "!=", '<',"<=", ">=", ">", "is", 'like', 'in', 'regexp']
    def __init__(self, table, db = None):
        self.query = None
        self.isExecuted = False
        self.error = None
        self.db = db
        self.isSelectQuery = False
        self.asDictionary = False

        self.column = None
        self.where_condition = None
        self.group_by = None
        self.having = None
        self.order_by = None
        self.limit = None
        self.offset = None

        self.table = table

    def printQ(self):
        print(">> ", self.query)

    def _where(self, condition = None):
        if condition:
            where_condition = condition
            if type(where_condition) in [tuple, list]:
                if not where_condition[0] in [Query._and, Query._or, Query._not]:
                    where_condition = Query._and(*where_condition)
            else:
                where_condition = Query._and(where_condition)
            return where_condition
        else: return Query._and((True,))

    def insert(self, data):
        self.isSelectQuery = False
        col = " ("
        val = " ("
        isFirst = True
        for key in data.keys():
            if isFirst:
                isFirst = False
            else:
                col += ","
                val += ","
            col += Query.colomnIdentity(key)
            val += Query._normailize(data[key])

        col += ") "
        val += ") "
        query = "INSERT INTO "+self.table+col+"VALUES"+val
        self.query = query
        if self.db == None:
            return self
        else:
            self.isExecuted = True
            return self.db.execute(self)

    def update(self, data, where = None):
        self.isSelectQuery = False
        where_condition = self._where(where)
        query = "UPDATE "+self.table+" SET "
        isFirst = True
        for key in data.keys():
            if isFirst:
                isFirst = False
            else:
                query += ","
            key = key.replace('`', '')
            query += Query.colomnIdentity(key)+" = "
            query += Query._normailize(data[key])
        query += "WHERE "+where_condition[1]
        self.query = query
        if self.db == None:
            return self
        else:
            self.isExecuted = True
            return self.db.execute(self)

    def delete(self, where = None):
        self.isSelectQuery = False
        where_condition = self._where(where)
        query = "DELETE FROM "+self.table+" WHERE "+where_condition[1]
        self.query = query
        if self.db == None:
            return self
        else:
            self.isExecuted = True
            return self.db.execute(self)
        
    def select(self, *column, **kwargs):
        self.asDictionary = asDictionary if 'asDictionary' in kwargs else False
        self.isSelectQuery = True
        isExecute = kwargs['isExecute'] if 'isExecute' in kwargs else True
        where = kwargs['where'] if 'where' in kwargs else True

        if len(column) > 0:         self.column     = column
        if 'group_by' in kwargs:    self.group_by   = kwargs['group_by']
        if 'having' in kwargs:      self.having     = kwargs['having']
        if 'order_by' in kwargs:    self.order_by   = kwargs['order_by']
        if 'limit' in kwargs:       self.limit      = kwargs['limit']
        if self.where_condition is None or where in kwargs:
            self.where_condition = self._where(where)
        
        self.query = 'SELECT '
        if not self.column:
            self.query += '*'
        else:
            isFirst = True
            for selected in self.column:
                if isFirst:
                    isFirst = False
                else:
                    self.query += ', '
                if type(selected) is str:
                    self.query += Query.colomnIdentity(selected)
                elif type(selected) in [tuple, list] and len(selected) > 0:
                    self.query += Query.colomnIdentity(selected[0])
                    if len(selected) > 1:
                        self.query += "AS "+ Query.colomnIdentity(selected[1])
        self.query += ' FROM '+self.table
        self.query += ' WHERE '+self.where_condition[1]
        
        if self.group_by:
            group_by_query = ''
            if type(self.group_by) not in [list, tuple]:
                self.group_by = [self.group_by]
            for grp_by in options["group_by"]:
                group_by_query += Query.colomnIdentity(grp_by)
            if group_by_query:  self.query += ' GROUP BY '+group_by_query
        
        if self.having:
            self.query += ' HAVING '+self.having

        if self.order_by:
            order_by_query = '' 
            if type(self.order_by) not in [list, tuple]:
                self.order_by = [self.order_by]
            isFirst = True
            for ord_by in self.order_by:
                if type(ord_by) is str:
                    order_by_query += ('' if isFirst else ',')+ Query.colomnIdentity(ord_by)
                    if isFirst: isFirst = False
                elif type(ord_by) in [tuple, list] and len(ord_by) > 0:
                    order_by_query += ('' if isFirst else ',')+ Query.colomnIdentity(ord_by[0])
                    order_by_query += (" "+ord_by[1] if len(ord_by)>1 else "")
                    if isFirst: isFirst = False
            if order_by_query: self.query += ' ORDER BY '+order_by_query

        if self.limit:
            limit_query = ''
            if type(self.limit) == int:
                limit_query = str(self.limit)
            elif type(self.limit) in [tuple, list] and len(self.limit) > 0:
                limit_query = str(self.limit[0])
                if len(self.limit) > 1:
                    limit_query += ','+ str(self.limit[1])
            if limit_query: self.query += ' LIMIT '+limit_query

        if self.db == None or not isExecute:
            return self
        else:
            self.isExecuted = True
            return self.db.execute(self)
    
    def getResult(self):
        if not self.isExecuted:
            return self
        if self.isSelectQuery:
            return self.db.execute(self)

    @staticmethod
    def colomnIdentity(col):
        return '.'.join(['`'+x+'`' for x in col.split('.')])

    @staticmethod
    def _normailize(val):
        if type(val) is str:
            return "'"+val.replace('\'', '\'\'')+"'"
        elif type(val) in [int, float]:
            return str(val)
        elif isinstance(val, Query):
            return '('+val.query+')'
        elif type(val) is list:
            return "(" + ','.join([Query._normailize(v) for v in val])+")"
        elif type(val) is bool:
            return 'TRUE' if val else 'FALSE'
        elif type(val) is type(None):
            return 'NULL'
        elif type(val) is datetime.date:
            return val.isoformat()
        elif type(val) is datetime.timedelta:
            return Query._secondsFormat(val.total_seconds())
        elif type(val) is datetime.time:
            val = datetime.datetime.combine(datetime.date.min, val) - datetime.datetime.min
            return Query._secondsFormat(val.total_seconds())
        elif type(val) is datetime.datetime:
            return val.isoformat()
        return 'TRUE'

    @staticmethod
    def _count(col = None):
        return Query._count, "COUNT({})".format("*" if not col else '.'.join(['`'+x+'`' for x in col.split('.')]))

    @staticmethod
    def _and(*arg):
        return Query._operation(True, *arg)

    @staticmethod
    def _or(*arg):
        return Query._operation(False, *arg)

    @staticmethod
    def _not(*arg):
        return Query._not, "NOT ("+Query._operation(True, *arg)[1]+")"

    @staticmethod
    def _secondsFormat(total_seconds):
        h=0
        m=0
        s=0
        h = int(total_seconds / 3600)
        total_seconds -= h * 3600
        m = int(total_seconds / 60)
        total_seconds -= m * 60
        s = int(total_seconds)
        return "{:d}:{:02d}:{:02d}".format(h,m,s)

    @staticmethod
    def _operation(isAnd, *arg):
        result = ""
        isFirst = True
        if type(arg) is not tuple:
            arg = (arg, )
        for x in arg:
            tmp_result = ''
            if type(x) is not tuple:
                x = (x,)
            if len(x) == 0:
                pass
            elif x[0] in [Query._and, Query._or, Query._not]:
                tmp_result += "("+x[1]+")"
            elif len(x) == 1:
                tmp_result += Query._normailize(x[0])
            elif len(x) == 2:
                tmp_result += Query.colomnIdentity(x[0])+" = "+ Query._normailize(x[1])
            elif len(x) == 3 and x[1].lower().replace(' ', '') in Query.operator:
                tmp_result += Query.colomnIdentity(x[0])+" "+x[1]+" "+Query._normailize(x[2])
            else:
                tmp_result += "FALSE"
            if tmp_result:
                if isFirst:
                    isFirst = False
                else:
                    result += " AND " if isAnd else " OR "
                result += tmp_result
        return (Query._and if isAnd else Query._or), result
'''
q = Query({
    "from":"name_table",
    "where": (
        "hey",
        ("key", "val"),
        ("key", "op", "val"),
        Query._not(
            ("key", "in", Query({
                "from": "student",
                "where": False
            }).select() ),
            ("key", "=", "val")
        )
    )
}).select()
q.printQ()
'''