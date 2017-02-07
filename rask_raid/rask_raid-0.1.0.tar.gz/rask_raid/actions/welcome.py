from hashlib import sha256
from rask.base import Base
from uuid import uuid4

__all__ = ['Welcome']

class Welcome(Base):
    def on_msg(self,msg,io):
        try:
            assert msg['header']['method'] == 'iam'
            assert msg['body']['name']
        except (AssertionError,KeyError):
            self.ioengine.loop.add_callback(io.close)
        except:
            raise
        else:
            io.__welcome_flag__ = True
            io.push({
                "header":{
                    "action":"raid.welcome",
                    "method":"take"
                },
                "body":{
                    "key":sha256('%s<%s>:%s' % (msg['body']['name'],msg['header']['__sysdate__'],uuid4().hex)).hexdigest()
                }
            })
        return True

