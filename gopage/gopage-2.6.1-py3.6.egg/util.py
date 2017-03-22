import functools


def cache(ctype=''):
    import json
    import pickle
    from os.path import exists

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            verbose = True
            usecache = True
            if 'cverbose' in kw:
                verbose = kw['cverbose']
                kw.pop('cverbose')
            if 'usecache' in kw:
                usecache = kw['usecache']
                kw.pop('usecache')
            if 'cache' in kw and not kw['cache']:
                kw.pop('cache')
                return func(*args, **kw)
            # read cache
            if usecache and 'cache' in kw and exists(kw['cache']):
                if verbose:
                    print('@{} reading cache'.format(func.__name__))
                if ctype == 'json':
                    with open(kw['cache']) as rf:
                        return json.load(rf)
                elif ctype == 'pickle':
                    with open(kw['cache'], 'rb') as rf:
                        return pickle.load(rf)
                elif ctype == 'text':
                    with open(kw['cache'], encoding='utf-8') as rf:
                        return rf.read()
            # create cache
            cachepath = None
            if 'cache' in kw:
                cachepath = kw['cache']
                kw.pop('cache')
            ret = func(*args, **kw)
            if cachepath:
                if verbose:
                    print('@{} creating cache'.format(func.__name__))
                if ctype == 'json':
                    with open(cachepath, 'w') as f:
                        json.dump(ret, f, indent=4)
                elif ctype == 'pickle':
                    with open(cachepath, 'wb') as f:
                        pickle.dump(ret, f)
                elif ctype == 'text':
                    with open(cachepath, 'w', encoding='utf-8') as f:
                        f.write(ret)
            return ret
        return wrapper
    return decorator
