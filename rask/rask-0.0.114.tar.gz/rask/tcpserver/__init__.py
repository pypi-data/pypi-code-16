from rask.base import Base
from tornado.tcpserver import TCPServer

__all__ = ['Server']

class Server(Base):  
    def __init__(self,on_connection,port=8810):
        self.on_connection = on_connection
        self.tcpserver.listen(port)

    @property
    def tcpserver(self):
        try:
            assert self.__tcpserver
        except (AssertionError,AttributeError):
            self.__tcpserver = TCPServer()
            self.__tcpserver.handle_stream = self.handle
        except:
            raise
        return self.__tcpserver

    def handle(stream,address):
        self.log.info('connection from %s:%s' % address)
        self.ioengine.loop.add_callback(
            self.on_connection,
            io=stream,
            address=address
        )
        return True
