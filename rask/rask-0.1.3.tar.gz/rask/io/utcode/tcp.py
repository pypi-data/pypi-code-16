from base64 import b64decode,b64encode
from rask.base import Base
from rask.options import options

__all__ = ['TCP']

class TCP(Base):
    @property
    def utcode(self):
        return options.utcode

    def decode(self,payload,future):
        def on_decode(_):
            return future.set_result(_.result())
        
        return self.utcode.decode(
            b64decode(payload.replace(':ut','')),
            future=self.ioengine.future(on_decode)
        )

    def encode(self,payload,future):
        def on_encode(_):
            return future.set_result('%s:ut' % b64encode(_.result()))
        
        return self.utcode.encode(
            payload,
            future=self.ioengine.future(on_encode)
        )
