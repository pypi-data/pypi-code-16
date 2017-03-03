from rask.base import Base

__all__ = ['FutureChain']

class FutureChain(Base):
    def __init__(self,done):
        self.done = done

    @property
    def bucket(self):
        try:
            assert self.__bucket
        except (AssertionError,AttributeError):
            self.__bucket = []
        except:
            raise
        return self.__bucket
        
    @property
    def future(self):
        f = self.ioengine.future(self.check)
        self.bucket.append(f)
        return f

    @property
    def results(self):
        return [f.result() for f in self.bucket]
    
    def check(self,_):
        for f in self.bucket:
            try:
                assert f.done()
            except AssertionError:
                return False
            except:
                raise

        try:
            assert self.done.done()
        except AssertionError:
            self.done.set_result(self.results)
        except:
            raise
        return True
