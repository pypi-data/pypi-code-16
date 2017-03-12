from rask.base import Base
from rask.options import options

__all__ = ['Welcome']

class Welcome(Base):
    def check_pattern(self,io,msg):
        try:
            assert msg.valid
            assert msg.payload['body']['_'] == 'raid'
            assert msg.payload['header']['action'] == 'raid.welcome'
        except (AssertionError,KeyError):
            io.close()
        except:
            raise
        else:
            io.__raid_online__()
            self.ioengine.loop.add_callback(
                self.talk_back,
                io=io,
                etag=msg.etag
            )
        return True

    def on_msg(self,io,*args,**kwargs):
        def on_decode(_):
            self.ioengine.loop.add_callback(
                self.check_pattern,
                io=io,
                msg=_.result()
            )
            return True
        
        return options.raid['envelop'].unpack(
            kwargs.get('msg',''),
            future=self.ioengine.future(on_decode)
        )

    def talk_back(self,io,etag):
        return io.push(
            options.raid['msg'](
                {
                    'body':{
                        '_':'raid'
                    },
                    'header':{
                        'action':'raid.ok',
                        'etag':etag
                    }
                }
            )
        )
