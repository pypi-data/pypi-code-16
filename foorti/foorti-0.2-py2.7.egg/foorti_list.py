from .foorti_systems import *

class List(redis_object):
    
    def right_append(self, item):
        self.conn.rpush(self.name, item)
    
    def left_append(self, item):
        self.conn.lpush(self.name, item)
        
    def left_remove(self):
        self.conn.lpop(self.name)
        
    def right_remove(self):
        self.conn.rpop(self.name)
        
    def list_len(self):
        self.conn.llen(self.name)
        
    def trim_list(self, start, stop):
        self.conn.ltrim(self.name, start, stop)