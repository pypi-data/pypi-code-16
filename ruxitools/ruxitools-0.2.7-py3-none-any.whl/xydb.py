#!/usr/bin/env python 
__author__ = "github.com/ruxi"
__copyright__ = "Copyright 2016, ruxitools"
__email__ = "ruxi.github@gmail.com"
__license__ = "MIT"
__status__ = "Development"
__version__ = "0.1"

from collections import namedtuple
class XyDB(object):
    """XyDB is a database-like containers for intermediate data

     The intended usecase of XyDB is to store intermediate data in a database-like
     container and bind it as an attribute to the source data. It solves the
     problem of namespace pollution by confining intermediate data forms to
     the original dataset in a logical and structured manner. The limitation
     of this object is that it exists in memory only. For more persistent storage
     solutions, its recommended to use an actual database library such as
     blaze, mongoDB, or SQLite. Conversely, the advantage is residual information
     is not left over after a session. 
     
    
     Example:
        Defined a namedtuple for input validation, then assign this function 
        as an attribute of your source data object, usually a pandas dataframe.
        
          import XyDB
          from collections import namedtuple
          
          # define input validation schema
          input_val = namedtuple("data", ['key','desc', 'X', 'y'])

          # define data
          myData = pd.DataFrame()
          
          # assign class function
          myData.Xy = XyDB(input_val, verbose = True)  
          
          # add data to DB
          myRecord = dict(key='config1'
                          , desc='dummydata'
                          , X=[0,1,0]
                          , y=['a','b','a])
          myData.Xy.push(**myRecord)
          
          # show data
          myData.Xy.config1.desc       

    """
    
    def __init__(self, schema = None, verbose=True, welcome=True):
        """
        Arguments:
            schema (default: None | NamedTuple):
                 
                Accepts a NamedTuple subclass with a "key" field
                which is used for input validation when records
                are "push"ed 
            

            verbose (default: True | boolean)
                
                If false, suppresses print commands. Including this message
                
            welcome (default: True | boolean)
            
                Suppresses printing of the docstring upon initialization
        """
        
        
        
        self._db = {}
        self._show = lambda: None
        self._pull = lambda: None
        self._verbose = verbose
        
        # print docstring
        if welcome:
            print (self.__doc__)

        
        # Input Validation (optional) can be spec'd out by NameTuple. 
        # Input NamedTuple requires 'key' field
        self._schema = False if schema is None else schema 
        if self._schema: 
            if "key" not in dir(self._schema):
                raise Exception("namedtuple must have 'key' as a field")
        

    #@db.setter
    def push(self, key, *args, **kwargs):
        """Adds records (dict) to database"""
        if not(type(key)==str):
            raise Exception('key must be string')
            
        # Create database record entry (a dict)
        if self._schema: # is user-defined 
            self._input_validator = self._schema          
            record =  self._input_validator(key, *args,**kwargs)
            
        else: # the schema is inferred from every push   
            entry_dict = dict(key=key, *args,**kwargs)
            self._input_validator = namedtuple('Data', list(entry_dict.keys()))
            record = self._input_validator(**entry_dict)
        
        # The record is added to the database.
        self._db[record.key] = record
        if self._verbose:
            print('Record added {}'.format(record.key))
        self._update()
        
    def _update(self):
        """updates dyanamic attribute access for self.show & self.pull"""
        for key in self.keys:
            # self.show.<key> = namedtuple
            setattr(self._show
                    , key
                    , self._db[key]
                   )     
            # self.pull.<key> = dict
            setattr(self._pull,
                    key,
                    self.db[key]._asdict() 
                   ) 
    @property
    def db(self):
        """Intermediate data accessible by keyword. Returns a dict"""
        return self._db               
                
    @property
    def keys(self):
        """
        list configuration keywords
        
        Returns:
            list
        """
        return self.db.keys()
    
    @property
    def show(self):
        """
        Show record from database. Accessible by attribute via keyname
        
        Returns:
            namedtuple objects  
        Usage: 
            show.<config keyword>.<attribute name>          
        """
        return self._show
        
    @property
    def pull(self):
        """
        Pull record from database. Accessible by attribute via keyname
           
        Returns:
            dictionary 
        Usage: 
            pull.<config keyword>
        """
        return self._pull        