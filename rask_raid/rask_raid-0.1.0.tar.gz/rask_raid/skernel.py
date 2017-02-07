from rask.base import Base

__all__ = ['SKernel']

class SKernel(Base):
    @property
    def connection(self):
        try:
            assert self.__connection
        except (AssertionError,AttributeError):
            self.__connection = {}
        except:
            raise
        return self.__connection

    def connection_add(self,_,io):
        self.connection[_] = io
        return True

    def connection_do(self,_,i=None):
        try:
            self.ioengine.loop.add_callback(
                _,
                i.next()
            )
        except AttributeError:
            self.ioengine.loop.add_callback(
                self.connection_do,
                _=_,
                i=iter(self.connection)
            )
        except StopIteration:
            return True
        except:
            raise
        else:
            self.ioengine.loop.add_callback(
                self.connection_do,
                _=_,
                i=i
            )
        return None
    
    def connection_del(self,_):
        try:
            assert self.connection[_]
        except (AssertionError,KeyError):
            pass
        except:
            raise
        else:
            del self.connection[_]
        return True
