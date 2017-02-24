from util import *

def run_once_for_each_obj(f):
  """decorate the method which only run once for each object
  """
  def wrapper(self,*args, **kwargs):
    if not hasattr(self,'_has_run'): self._has_run={}
    if f.__name__ in self._has_run:
      raise Exception('%s Only Allow Run Once'%f.__name__)
    else:
      self._has_run[f.__name__] = True
      return f(self,*args, **kwargs)
  wrapper.__name__ = f.__name__
  return wrapper


