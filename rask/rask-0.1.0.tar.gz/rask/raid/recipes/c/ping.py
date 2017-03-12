from rask.base import Base
from rask.options import options
from rask.parser.date import datetime_float_str

__all__ = ['Ping']

class Ping(Base):
    def on_msg(self,io,*args,**kwargs):
        return io.push(
            options.raid['msg'](
                {
                    'body':{
                        '_':datetime_float_str()
                    },
                    'header':{
                        'action':'pong'
                    }
                }
            )
        )
