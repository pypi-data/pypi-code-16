from rask.http import WSHandler
from rask.parser.date import datetime2timestamp
from rask.parser.utcode import UTCode
from rask_raid.actions import ACTIONS
import udatetime

__all__ = ['Handler']

class Handler(WSHandler):
    @property
    def actions(self):
        try:
            assert self.__actions
        except (AssertionError,AttributeError):
            self.__actions = {
                'ping':self.__ping__
            }
            self.__actions.update(ACTIONS)
        except:
            raise
        return self.__actions
    
    @property
    def options(self):
        try:
            assert self.__options
        except (AssertionError,AttributeError):
            self.__options = {
                'code':{
                    'ws':{
                        'ns':{
                            'invalid':'acff04b473ce47d7ad6115454d887ff6'
                        },
                        'payload':{
                            'invalid':'cec3aff19fd2449097a02697b39c162c'
                        }
                    }
                }
            }
        except:
            raise
        return self.__options

    def __ping__(self,msg,io):
        self.push({
            'header':{
                'action':'ping'
            }
        })
        return True
    
    def call(self,msg):
        try:
            assert msg['header']['action'] in self.actions
        except (AssertionError,KeyError):
            self.error(
                self.options['code']['ws']['ns']['invalid'],
                msg.get('header',{}).get('etag',None)
            )
        except:
            raise
        else:
            self.ioengine.loop.add_callback(
                self.actions[msg['header']['action']],
                msg=msg,
                io=self
            )
        return True

    def error(self,code,etag=None):
        self.push({
            "header":{
                "action":"error",
                "code":str(code),
                "etag":str(etag)
            }
        })
        return True
    
    def on_message(self,msg):
        def on_decode(_):
            try:
                assert _.result()['header']['__sysdate__']
            except (AssertionError,AttributeError,KeyError):
                self.error(self.options['code']['ws']['payload']['invalid'])
            except:
                raise
            else:
                self.ioengine.loop.add_callback(
                    self.welcome_check,
                    msg=_.result()
                )
            return True
        
        self.utcode.decode(msg,future=self.ioengine.future(on_decode))
        return True
    
    def open(self):
        self.utcode = UTCode()

        self.log.info('connected: %s [%s]' % (self.request.remote_ip,self.uuid))        
        self.set_nodelay(True)
        self.ioengine.loop.add_callback(self.on_open)
        self.push({"header":{"action":"raid.welcome","method":"who"}})
        return True

    def on_close(self):
        pass
        
    def on_open(self):
        pass
    
    def push(self,_):
        def on_encode(payload):
            self.write_message(payload.result())
            return True

        _['header']['__sysdate__'] = datetime2timestamp(udatetime.utcnow())
        self.utcode.encode(_,future=self.ioengine.future(on_encode))
        return True

    def welcome_check(self,msg):
        try:
            assert self.__welcome_flag__
        except (AssertionError,AttributeError):
            self.ioengine.loop.add_callback(
                self.actions['raid.welcome'],
                msg=msg,
                io=self
            )
        except:
            raise
        else:
            self.ioengine.loop.add_callback(
                self.call,
                msg=msg
            )
        return True
