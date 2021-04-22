import datetime
from bson.objectid import ObjectId

class ModelIterator:
    def __init__(self, model_class, cursor):
        self.model_class = model_class
        self.cursor = cursor

    def limit(self, num):
        self.cursor.limit(num)
        return self

    def page(self, num, limit = 20):
        return self

    def __iter__(self):
        return self

    def __next__(self):
        model = self.cursor.__next__()
        return self.model_class.createFromDict(model, False)

class Model(object):
    DB = None
    COLLECTION = None
    KEY = None
    PRIMARY_KEY = '_id'
    WHERE = {}
    Databases = {}
    Log = None

    def __init__(self, *arg, **kw):
        self.__id = None
        self.__updated__attr = {}
        self.__attributtes = self._attributtes()
        self.__relations = {}
        self.__generate__attrs()

        for key in kw.keys():
            setattr(self, key, kw[key])

    def _attributtes(self):
        return {}
    
    def _getUpdatedAttr(self):
        new_data = self.__updated__attr
        for attr in self.__attributtes:
            if self.__attributtes[attr]['datatype'] == 'dict':
                object_model = getattr(self, attr, None)
                if object_model:
                    object_new_data = object_model._getUpdatedAttr()
                    for object_key in object_new_data:
                        new_data[attr+"."+object_key] = object_new_data[object_key]
        return new_data
    
    def save(self):
        db = self.Databases[self.DB][self.COLLECTION]
        if self.__id is None:
            result = db.insert_one(dict(self))
            if result is not None:
                self.__id = result.inserted_id
                setattr(self, self.PRIMARY_KEY, self.__id)
                return True
        else:
            updated_data = {}
            result = db.update_one(self.__updated__attr,
                where=[(self.PRIMARY_KEY, self.__id)]
            )
            return result.result

    def delete(self):
        db = self.Databases[self.DB][self.COLLECTION]
        if self.__id is not None:
            result = db.delete(where=[(self.PRIMARY_KEY, self.__id)])
            if result is not None:
                return True

    def __generate__attrs(self):
        _attrs = self.__attributtes
        if self.PRIMARY_KEY in _attrs.keys():
            _attrs[self.PRIMARY_KEY]['primary'] = True
        for _key in _attrs.keys():
            setattr(self, _key, _attrs[_key]["default"] if "default" in _attrs[_key] else None)

    def __iter__(self):
        data = {}
        for attr in self.__attributtes:
            if self.__attributtes[attr]['datatype'] == 'dict':
                yield (attr, dict(getattr(self, attr)))
            elif self.__attributtes[attr]['datatype'] == 'list':
                yield (attr, list(getattr(self, attr)))
            elif attr == self.PRIMARY_KEY:
                if self.__id is not None:
                    yield (attr, getattr(self, attr))
            else:
                yield (attr, getattr(self, attr))

    def __setattr__(self, name, value):
        if name in self.WHERE:
            value = self.WHERE[name]
        if (hasattr(self, "_Model__attributtes") 
         and name in self.__attributtes 
         and "datatype" in self.__attributtes[name]
        ):
            datatype = self.__attributtes[name]["datatype"]
            new_value = None
            if value is None:
                new_value = value
            elif datatype == 'int':
                new_value = int(value)
            elif datatype == 'float':
                new_value = float(value)
            elif datatype == 'str':
                new_value = str(value)
            elif datatype == 'object_id':
                if value is None:
                    new_value = ObjectId()
                elif type(value) is bytes:
                    new_value = ObjectId(value)
                elif type(value) is str:
                    new_value = ObjectId(bytes(value))
                else:
                    new_value = value
            elif datatype == 'date':
                if type(value) is str:
                    new_value = datetime.datetime.strptime(value, '%Y-%m-%d').date()
                elif type(value) is int:
                    new_value = datetime.date.fromtimestamp(value)
                elif type(value) is datetime.date:
                    new_value = value
                else:
                    new_value = None
            elif datatype == 'list':
                if type(value) is list:
                    new_value = ModelList(value)
            elif datatype == 'dict':
                if type(value) is dict:
                    new_value = ModelObject(
                        name,
                        self.__attributtes[name]["attributes"], 
                        **value
                    )
                    new_value.DB = self.DB
                    new_value.COLLECTION = self.COLLECTION
            if datatype not in ['list', 'dict']:
                self.__updated__attr[name] = new_value
            return object.__setattr__(self, name, new_value)
        return object.__setattr__(self, name, value)

    def __getattribute__(self, name):
        if (name != '_Model__attributtes'
         and hasattr(self, "_Model__attributtes") 
         and name in self.__attributtes 
         and "datatype" in self.__attributtes[name]
        ):
            datatype = self.__attributtes[name]["datatype"]
        return object.__getattribute__(self, name)

    @classmethod
    def create(this_class, *arg, **kw):
        model = this_class(*arg, **kw)
        return model

    @classmethod
    def createFromDict(this_class, args, is_new = True):
        model = this_class(**args)
        if not is_new:
            model.__updated__attr = {}
            if this_class.PRIMARY_KEY in args.keys():
                model.__id = args[this_class.PRIMARY_KEY]
        return model

    @classmethod
    def first(this_class, *arg, **args):
        db = this_class.Databases[this_class.DB]
        _where = {}
        for key in args.keys():
            _where[key] = {"$eq": args[key]}
        for key in this_class.WHERE.keys():
            _where[key] = {"$eq": this_class.WHERE[key]}
        result = db[this_class.COLLECTION].find_one(_where)
        model = None
        if result:
            model = this_class.createFromDict(result, False)
        return model

    @classmethod
    def all(this_class):
        db = this_class.Databases[this_class.DB]
        cursor = db[this_class.COLLECTION].find()
        return ModelIterator(this_class, cursor)
        
    @classmethod
    def search(this_class, *arg, **args):
        db = this_class.Databases[this_class.DB]
        _where = {}
        for key in args.keys():
            _where[key] = {"$eq": args[key]}
        for key in this_class.WHERE.keys():
            _where[key] = {"$eq": this_class.WHERE[key]}
        cursor = db[this_class.COLLECTION].find(_where)
        return ModelIterator(this_class, cursor)

    @staticmethod
    def _integer(default = 0):
        return {
            "datatype" : "int",
            "default": int(default)
        }

    @staticmethod
    def _float(default = 0.0):
        return {
            "datatype" : "float",
            "default": float(default)
        }

    @staticmethod
    def _string(default = None):
        return {
            "datatype" : "str",
            "default": str(default) if default else None
        }

    @staticmethod
    def _date(default = None):
        return {
            "datatype" : "date",
            "default": default
        }

    @staticmethod
    def _time(default = None):
        return {
            "datatype" : "time",
            "default": default
        }

    @staticmethod
    def _datetime(default = None):
        return {
            "datatype" : "datetime",
            "default": default
        }

    @staticmethod
    def _object_id(default = None):
        return {
            "datatype" : "object_id",
            "default": default
        }

    @staticmethod
    def _list(listof, default = []):
        return {
            "datatype" : "list",
            "listof" : listof,
            "default": default
        }

    @staticmethod
    def _object(attributes, default = {}):
        return {
            "datatype" : "dict",
            "attributes" : attributes,
            "default": default
        }

class ModelObject(Model):
    def __init__(self, key, attributes, **kw): 
        self.KEY = key
        def attr():
            return attributes
        self._attributtes = attr
        Model.__init__(self, *(), **kw)
    
    def save(self): pass
    
    def delete(self): pass

class ModelList:
    def __init__(self, data): 
        self.data = data
        self.i = -1
    
    def __iter__(self):
        self.i = -1
        return self

    def __next__(self):
        self.i += 1
        if self.i >= len(self.data):
            raise StopIteration
        return self.data[self.i]
