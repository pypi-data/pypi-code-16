from rask.base import Base
from rask.concurrent import FutureChain

__all__ = ['RMap']

class RMap(Base):
    @property
    def data(self):
        try:
            assert self.__data
        except (AssertionError,AttributeError):
            self.__data = {}
        except:
            raise
        return self.__data

    def __dict_load_flags__(self,d,i,future):
        try:
            k = str(i.next())
            assert d[k]
        except AssertionError:
            self.db.flags[k].disable()
        except StopIteration:
            future.set_result(True)
            return True
        except:
            raise
        else:
            self.db.flags[k].enable()

        self.ioengine.loop.add_callback(
            self.__dict_load_flags__,
            d=d,
            i=i
        )
        return None

    def __dict_load_registers__(self,d,i,future):
        try:
            k = str(i.next())
        except StopIteration:
            future.set_result(True)
            return True
        except:
            raise
        else:
            self.db.registers[k].assign(d[k])

        self.ioengine.loop.add_callback(
            self.__dict_load__registers__,
            d=d,
            i=i,
            future=future
        )
        return None
    
    def dict_load(self,d,future):
        fchain = FutureChain(done=future)
        
        self.__dict_load_flags__(
            d=d.get('flags',{}),
            i=iter(d.get('flags',[])),
            future=fchain.future
        )

        self.__dict_load_registers__(
            d=d.get('registers',{}),
            i=iter(d.get('registers',[])),
            future=fchain.future
        )
        return True
