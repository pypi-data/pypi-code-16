from rask.http import WSHandler
from rask.parser.date import datetime_float_str
from rask.options import options

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

    def __on_message__(self,msg):
        def on_decode(_):
            try:
                assert _.result().valid
                assert _.result().action in options.raid['recipes']
            except (AssertionError,AttributeError):
                self.error(
                    self.options['code']['ws']['payload']['invalid']
                )
            except:
                raise
            else:
                options.raid['recipes'][_.result().action](
                    io=self,
                    msg=_.result()
                )
            return True

        options.raid['envelop'].unpack(
            msg=msg,
            future=self.ioengine.future(on_decode)
        )
        return True
    
    def __on_message_hi__(self,msg):
        options.raid['recipes']['s']['raid.welcome'](
            io=self,
            msg=msg
        )
        return True

    def __raid_online__(self):
        self.on_message = self.__on_message__
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
        self.push(
            options.raid['msg'](
                {
                    "header":{
                        "action":"error",
                        "code":str(code),
                        "etag":str(etag)
                    }
                }
            )
        )
        return True
    
    def on_message(self,msg):
        pass
    
    def open(self):
        self.log.info(
            '<raid> connected: %s [%s]' % (
                self.request.remote_ip,
                self.uuid
            )
        )
        self.set_nodelay(True)
        self.on_message = self.__on_message_hi__
        options.raid['recipes']['s']['raid.hi'](self)
        return self.ioengine.loop.add_callback(self.on_open)

    def on_close(self):
        pass
        
    def on_open(self):
        pass
    
    def push(self,_):
        def on_encode(payload):
            self.write_message(payload.result())
            return True

        _.payload['header']['__sysdate__'] = datetime_float_str()
        return options.raid['envelop'].pack(
            _,
            self.ioengine.future(on_encode)
        )

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
