from tinydb import TinyDB, Query


def model(modelclass):
    """ 
        Class decorator granting tinymodel API compatibility.
        Only classes that have pure **kwargs constructors are supported.
    """
    
    class TinyModel(modelclass):
        """ Mixin with dict serialization and deserialization methods. """
        
        is_tinymodel = True
        
        def asdict(self):
            """ Serializes object into a Python dictionary. """
            return self.__dict__
        
        @classmethod
        def fromdict(cls, dict_):
            """ Deserializes object from a Python dictionary. """
            return cls(**dict_)
    
    TinyModel.__name__ = modelclass.__name__
    TinyModel.__doc__ = modelclass.__doc__
    return TinyModel

db = None
def connect(path):
    """ Instantiates and returns the module-level TinyDB instance. """
    global db
    db = TinyDB(path)
    return db

def save(tinyobj):
    """
        Inserts or updates a tinymodel instance into the database.
        Each tinymodel class has its own table, and each instance is
        stored in its class' table.
        
        A unique field on the object is used to determine whether to insert or update.
        If the unique field name is not provided by the caller, the field 'key' is used.
        If no key field exists, then the id of the object is used.
    """
    
    global db
    if not tinyobj.__class__.is_tinymodel:
        raise ValueError("{} of class {} is not a TinyModel class. Please decorate it with @tinymodel.tinymodel".format(tinyobj, tinyobj.__class__.__name__))

    table = db.table(tinyobj.__class__.__name__)
    key_field = getattr(tinyobj.__class__, 'key_field', 'key')
    key = getattr(tinyobj, key_field, id(tinyobj))

    if key:
        res = table.search(Query()[key_field] == key)
        if len(res) > 0:
            table.update(tinyobj.asdict(), Query()[key_field] == key)
            print(table.all())
        else:
            table.insert(tinyobj.asdict())
    else:
        table.insert(tinyobj.asdict())

def load(tinyclass, *, where=None, empty_callback=None):
    """
        Loads all instances of TinyClass, returning the set as an iterator of deserialized instances.
        
        :where: if not specified, all instances are returned.
        
        :empty_callback: performed if no instances are found.
    """
    
    global db
    table = db.table(tinyclass.__name__)
    
    if not where:
        res = table.all()
    else:
        res = table.search(where(Query()))
        
    if len(res) > 0:
        return (tinyclass.fromdict(item) for item in res)
    else:
        if empty_callback:
            return empty_callback()
        else:
            return None