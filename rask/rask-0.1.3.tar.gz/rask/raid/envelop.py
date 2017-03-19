from rask.base import Base
from rask.options import options

__all__ = ['Envelop']

class Envelop(Base):
    @property
    def msg(self):
        return options.raid['msg']
    
    @property
    def utcode(self):
        return options.utcode

    def pack(self,msg,future):
        try:
            assert msg.valid
        except AssertionError:
            future.set_result(False)
            return False
        except:
            raise

        def on_encode(_):
            future.set_result(_.result())
            return True
        
        return self.utcode.encode(
            msg.payload,
            future=self.ioengine.future(on_encode)
        )
    
    def unpack(self,msg,future):
        def on_decode(_):
            future.set_result(
                self.msg(
                    payload=_.result()
                )
            )
            return True
        
        return self.utcode.decode(
            msg,
            future=self.ioengine.future(on_decode)
        )
