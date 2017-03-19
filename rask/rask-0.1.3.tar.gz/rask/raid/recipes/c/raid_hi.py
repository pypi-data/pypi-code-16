from rask.base import Base
from rask.options import options

__all__ = ['Hi']

class Hi(Base):
    @property
    def msg(self):
        return options.raid['msg']({
            'body':{
                '_':'raid'
            },
            'header':{
                'action':'raid.welcome'
            }
        })
    
    def on_msg(self,io,*args,**kwargs):
        return io.push(self.msg)
