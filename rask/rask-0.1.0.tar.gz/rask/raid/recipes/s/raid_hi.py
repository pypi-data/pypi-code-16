from rask.base import Base
from rask.options import options

__all__ = ['Hi']

class Hi(Base):
    def __init__(self):
        self.__msg = options.raid['msg']({
            'body':{
                '_':'raid'
            },
            'header':{
                'action':'raid.hi'
            }
        })

    @property
    def msg(self):
        return self.__msg
    
    def on_msg(self,io,*args,**kwargs):
        return io.push(self.msg)
