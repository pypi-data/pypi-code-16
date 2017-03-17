from rask.base import Base
from rask.options import options

__all__ = ['Ping']

class Ping(Base):
    def on_msg(self,io,*args,**kwargs):
        return io.push(
            options.raid['msg'](
                {
                    'body':{
                        '_':True
                    },
                    'header':{
                        'action':'ping'
                    }
                }
            )
        )
