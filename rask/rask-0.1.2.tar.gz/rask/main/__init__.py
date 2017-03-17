from rask.base import Base
from rask.options import define,options,parse_command_line
from rask.parser.json import dictfy
from rask.parser.utcode import UTCode
from tornado.httpclient import AsyncHTTPClient,HTTPRequest
from tornado.web import Application

__all__ = ['Main']

class Main(Base):
    __http__ = None
    __http_routes__ = []
    __options__ = {
        'rmq':{
            'channel':{
                'prefetch':10
            }
        }
    }
    __settings_decoders = {
        'json':dictfy
    }

    def __init__(self):
        self.before()
        self.setup()
        self.ioengine.loop.add_callback(self.after)
        self.ioengine.loop.add_callback(self.http)
        self.ioengine.start()

    @property
    def http_client(self):
        try:
            assert self.__http_client
        except (AssertionError,AttributeError):
            self.__http_client = AsyncHTTPClient()
        except:
            raise
        return self.__http_client.fetch

    @property
    def http_request(self):
        return HTTPRequest(
            allow_nonstandard_methods=True,
            request_timeout=20,
            url='http://localhost',
            validate_cert=False
        )
    
    @property
    def services(self):
        try:
            assert self.__services
        except (AssertionError,AttributeError):
            self.__services = {}
        except:
            raise
        return self.__services

    @property
    def utcode(self):
        try:
            assert self.__utcode
        except (AssertionError,AttributeError):
            self.__utcode = UTCode()
        except:
            raise
        return self.__utcode
    
    def __settings_file_read(self,name):
        try:
            rfile = open(name,'r')
            rcontent = rfile.read()
            rfile.close()
        except IOError:
            self.log.error('IOError on %s open file, stopping IOEngine...' % name)
            self.ioengine.stop()
            return False
        except:
            raise
        return rcontent

    def __setup_autoreload(self):
        try:
            assert options.autoreload
        except AssertionError:
            pass
        except:
            raise
        else:
            self.log.info('autoreload: start')
            
            from tornado import autoreload
            autoreload.start()
        return True
    
    def after(self):
        pass

    def before(self):
        pass

    def http(self):
        try:
            assert self.__http_routes__
        except AssertionError:
            return False
        except:
            raise
        else:
            self.__http__ = Application(self.__http_routes__)
            self.ioengine.loop.add_callback(
                self.__http__.listen,
                port=options.http_port,
                xheaders=True
            )
            self.log.info('HTTP Server - %s' % options.http_port)
        return True

    def services_init(self):
        pass
    
    def setup(self):
        define('autoreload',default=False)
        define('http_port',default=8088)
        define('rask',default=self.__options__)
        define('raven_color',default=True)
        define('raven_color_fmt',default='%(log_color)s%(levelname)1.1s %(asctime)s %(name)s%(reset)s %(message)s')
        define('raven_no_color_fmt',default='%(levelname)1.1s %(asctime)s %(name)s %(message)s')
        define('utcode',default=self.utcode)

        self.setup_raid()
        parse_command_line()
        
        self.ioengine.loop.add_callback(self.__setup_autoreload)
        return True

    def setup_raid(self):
        from rask.raid.envelop import Envelop as RaidEnvelop
        from rask.raid.handler import Handler as RaidHandler
        from rask.raid.msg import MSG as RaidMSG
        from rask.raid.recipes.c import Hi,Ping
        
        define('raid',default={
            'code':{
                'ns:invalid':'acff04b473ce47d7ad6115454d887ff6',
                'payload:invalid':'cec3aff19fd2449097a02697b39c162c'
            },
            'envelop':RaidEnvelop(),
            'handler':RaidHandler,
            'msg':RaidMSG,
            'recipes':{
                'c':{
                    'ping':Ping().on_msg,
                    'raid.hi':Hi().on_msg
                }
            }
        })
        return True
    
    def settings_load(self,name,f_name,encode='json',future=None):
        try:
            define(
                name,
                default=self.__settings_decoders[encode](self.__settings_file_read(f_name))
            )
        except KeyError:
            self.log.info('Settings load, no encode (%s) found, stopping IOEngine...' % encode)
            self.ioengine.stop()
        except:
            raise
        else:
            self.log.info('Settings %s loaded...' % name)

        try:
            future.set_result(True)
        except:
            pass            
        return True
