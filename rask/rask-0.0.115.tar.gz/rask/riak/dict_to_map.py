from rask.base import Base
from rask.concurrent import FutureChain

__all__ = ['DictToMap']

class DictToMap(Base):
    def __init__(self,data,target,future):
        self.target = target
        
        def on_fchain(_):
            future.set_result(self.target)
            return True
        
        fchain = FutureChain(done=self.ioengine.future(on_fchain))

        self.__dict_load_flags__(
            d=data.get('flags',{}),
            i=iter(data.get('flags',[])),
            future=fchain.future
        )

        self.__dict_load_registers__(
            d=data.get('registers',{}),
            i=iter(data.get('registers',[])),
            future=fchain.future
        )

    def __dict_load_flags__(self,d,i,future):
        try:
            k = str(i.next())
            assert d[k]
        except AssertionError:
            self.target.flags[k].disable()
        except StopIteration:
            future.set_result(True)
            return True
        except:
            raise
        else:
            self.target.flags[k].enable()

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
            self.target.registers[k].assign(d[k])

        self.ioengine.loop.add_callback(
            self.__dict_load__registers__,
            d=d,
            i=i,
            future=future
        )
        return None

