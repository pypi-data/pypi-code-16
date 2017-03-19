from rask.parser.date import datetime_float_str
from rask.base import Base

__all__ = ['MSG']

class MSG(Base):
    def __init__(self,payload):
        self.payload = payload

    @property
    def action(self):
        try:
            assert self.payload['header']['action']
        except (AssertionError,AttributeError,KeyError):
            return None
        except:
            raise
        return self.payload['header']['action']

    @action.setter
    def action(self,_):
        try:
            self.payload['header']['action'] = str(_)
        except:
            raise
        
    @property
    def body(self):
        try:
            assert self.payload['body']
        except (AssertionError,AttributeError,KeyError):
            self.payload['body'] = {}
        except:
            raise
        return self.payload['body']

    @body.setter
    def body(self,_):
        try:
            assert isinstance(_,dict)
        except:
            raise
        else:
            self.payload['body'] = _
        
    @property
    def code(self):
        try:
            assert self.payload['header']['code']
        except (AssertionError,AttributeError,KeyError):
            return None
        except:
            raise
        return self.payload['header']['code']

    @code.setter
    def code(self,_):
        try:
            self.payload['header']['code'] = str(_)
        except:
            raise

    @property
    def etag(self):
        try:
            assert self.payload['header']['etag']
        except (AssertionError,AttributeError,KeyError):
            self.payload['header']['etag'] = self.uuid
        except:
            raise
        return self.payload['header']['etag']

    @etag.setter
    def etag(self,_):
        try:
            self.payload['header']['etag'] = str(_)
        except KeyError:
            self.payload['header'] = {'etag':str(_)}
        except:
            raise
        
    @property
    def payload(self):
        try:
            assert self.__payload
        except AttributeError:
            self.__payload = {
                'body':{},
                'header':{
                    'code':None,
                    'etag':None
                }
            }
        except:
            raise
        return self.__payload

    @payload.setter
    def payload(self,_):
        try:
            assert isinstance(_,dict)
        except:
            raise
        else:
            self.__payload = _

    @property
    def sysdate(self):
        try:
            assert self.__payload['header']['__sysdate__']
        except (AttributeError,KeyError):
            self.__payload['header']['__sysdate__'] = datetime_float_str()
        except:
            raise
        return self.__payload['header']['__sysdate__']

    @sysdate.setter
    def sysdate(self,_):
        self.__payload['header']['__sysdate__'] = _
            
    @property
    def valid(self):
        try:
            assert self.action
            assert self.etag
            assert self.sysdate
        except AssertionError:
            return False
        except:
            raise
        return True
