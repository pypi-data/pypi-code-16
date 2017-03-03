from functools import reduce, wraps
import collections

def requires_context(fn):
    fn.requires_context = True
    return fn

def is_seq(v):
    return isinstance(v, collections.Iterable)

def is_pred(pred):
    def w1(fn):
        @wraps(fn)
        def w2(v):
            if not pred(v):
                raise ValueError("given value %r fails predicate %r" % (v, pred.__name__))
            return fn(v)
        return w2
    return w1

is_str = is_pred(lambda v: isinstance(v, str))

def do_all_if_tuple(fn):
    @wraps(fn)
    def wrapper(v):
        if isinstance(v, tuple):
            return tuple([fn(x) for x in v])
        return fn(v)
    return wrapper

@do_all_if_tuple
@is_str
def uppercase(v):
    return v.upper()

@do_all_if_tuple
@is_str
def lowercase(v):
    return v.lower()

@do_all_if_tuple
@is_str
def titlecase(v):
    return v.title()

class PipelineError(Exception):
    pass

def pipeline(*pline):
    """a wrapper around the typical list that helps with debugging
    
    usage: 
      description = {'foo': pipeline(123, et3.utils.lowercase)}
      et3.render(description)"""
    def wrapper(processor, item):
        try:
            return processor(item, pline)
        except Exception as err:
            def forn(x):
                if hasattr(x, '__name__'):
                    return 'fn:' + x.__name__
                return str(x)
            msg = "pipeline %r failed with: %s" % ([forn(v) for v in pline], err)
            # LOG.error(doi(item) + " - caught exception attempting to render: " + msg)
            raise PipelineError(msg)
    return wrapper
