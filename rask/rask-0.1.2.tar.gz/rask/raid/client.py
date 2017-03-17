from rask.base import Base
from rask.options import options
from rask.parser.date import datetime_float_str
from tornado.websocket import websocket_connect

__all__ = ['Client']

class Client(Base):
    def __init__(self,url):
        self.__connection = websocket_connect(
            url,
            connect_timeout=10.0,
            on_message_callback=self.__on_message__
        )

    @property
    def connection(self):
        try:
            assert self.__connection.result()
        except AssertionError:
            return self.__connection
        except:
            raise
        return self.__connection.result()
        
    def __on_message__(self,body):
        try:
            assert body
        except AssertionError:
            self.ioengine.loop.add_callback(
                self.on_close
            )
            return False
        except:
            raise
        
        def on_decode(_):
            return self.ioengine.loop.add_callback(
                self.__on_message_recipes__,
                msg=_.result()
            )
        
        return options.raid['envelop'].unpack(
            body,
            future=self.ioengine.future(on_decode)
        )

    def __on_message_recipes__(self,msg):
        try:
            assert msg.action in options.raid['recipes']['c']
        except (AssertionError,KeyError):
            self.ioengine.loop.add_callback(
                self.on_msg,
                msg=msg
            )
            return False
        except:
            raise
        return self.ioengine.loop.add_callback(
            options.raid['recipes']['c'][msg.action],
            io=self,
            msg=msg
        )            

    def on_close(self):
        pass
    
    def on_msg(self,msg):
        pass

    def push(self,_):
        def on_encode(payload):
            self.connection.write_message(payload.result())
            return True

        _.payload['header']['__sysdate__'] = datetime_float_str()        
        return options.raid['envelop'].pack(
            _,
            self.ioengine.future(on_encode)
        )
