from rask.base import Base
from rask.options import options
from recipes.s import Hi,Ping,Welcome

__all__ = ['Raid']

class Raid(Base):
    def __init__(self):
        self.ioengine.loop.add_callback(self.__setup__)

    @property
    def bucket(self):
        try:
            assert self.__bucket
        except (AssertionError,AttributeError):
            self.__bucket = {}
        except:
            raise
        return self.__bucket
    
    @property
    def connections(self):
        try:
            assert self.__connections
        except (AssertionError,AttributeError):
            self.__connections = []
        except:
            raise
        return self.__connections

    @property
    def envelop(self):
        return options.raid['envelop']

    @property
    def handler(self):
        return options.raid['handler']
    
    @property
    def msg(self):
        return options.raid['msg']
    
    def __setup__(self):
        options.raid['bus'] = self
        options.raid['recipes']['s'] = {
            'ping':Ping().on_msg,
            'raid.hi':Hi().on_msg,
            'raid.welcome':Welcome().on_msg
        }
        return True
    
    def bucket_add(self,b,k,v):
        try:
            self.bucket[b][k] = v
        except KeyError:
            self.bucket[b] = {k:v}
        except:
            raise
        return True

    def bucket_broadcast(self,b,payload,i=None):
        try:
            self.bucket[b][i.next()].push(payload)
        except AttributeError:
            self.ioengine.loop.add_callback(
                self.bucket_broadcast,
                b=b,
                payload=payload,
                i=iter(self.bucket.get(b,[]))
            )
        except KeyError:
            self.ioengine.loop.add_callback(
                self.bucket_broadcast,
                b=b,
                payload=payload,
                i=i
            )
        except StopIteration:
            return True
        except:
            raise
        else:
            self.ioengine.loop.add_callback(
                self.bucket_broadcast,
                b=b,
                payload=payload,
                i=i
            )
        return None
    
    def bucket_del(self,b,k):
        try:
            del self.bucket[b][k]
            assert self.bucket[b]
        except AssertionError:
            del self.bucket
        except KeyError:
            pass
        except:
            raise
        return True
    
    def connections_add(self,_):
        self.connections.append(_)
        return True

    def connections_broadcast(self,payload,i=None):
        try:
            i.next().push(payload)
        except AttributeError:
            self.ioengine.loop.add_callback(
                self.connections_broadcast,
                payload=payload,
                i=iter(self.connections)
            )
        except StopIteration:
            return True
        except:
            raise
        else:
            self.ioengine.loop.add_callback(
                self.connections_broadcast,
                payload=payload,
                i=i
            )
        return None
    
    def connections_del(self,_):
        self.connections.remove(_)
        return True

    def recipes_update(self,_):
        return True
