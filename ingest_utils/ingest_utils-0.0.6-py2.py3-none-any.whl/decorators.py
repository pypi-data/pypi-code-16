def timeit(method):
    """ Returns time of delta for function in seconds """

    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        delta = round((te - ts), 1)
        if delta > 1:
            t = ' '.join([str(delta), 's'])
        else:
            t = ' '.join([str(round((te - ts) * 1000, 1)), 'ms'])

        print('Function', method.__name__, 'time:', t)
        print()
        return round((te - ts), 2)

    return timed


from memory_profiler import profile as mem
from IPython.core import display as ICD


def pandas_print(func):
    """ Helps make more printing in Pandas """
    top5 = []

    def wrapper():
        print(top5)
        for f in func():
            if isinlstance(f, dict):
                top5.append(f)
                continue
            elif isinstance(f, pd.core.frame.DataFrame) or isinstance(
                    f, pd.core.series.Series):
                ICD.display(f)

            elif isinstance(f, tuple):
                print([x for x in f])

            else:
                print(f)
            print(u'\n')
        t5 = pd.DataFrame(top5)
        if "Unique Values" in t5.columns:
            t5 = t5.sort_values(
                by="Unique Values", inplace=True, ascending=False)
            return wrapper(t5)

    return wrapper


from io import StringIO
from contextlib import redirect_stdout


def silence(method):
    """ 
    Silences print statements by directing to a return statement.
    Also returns anything returned by the function. 
    Returns ("print buffer","return from original function")
    """

    def wrapper():
        with StringIO() as buf, redirect_stdout(buf):
            value = ''
            value = method()
            print('redirected', method.__name__)
            return buf.getvalue(), value

    return wrapper

from pprint import pprint
def lazy_pprint(func):
    ''' Pure sugar. Print to stdout with just yield '''

    def wrapper(*args):
        for f in func(*args):
            pprint(f)

    return wrapper

def lazy_print(func):
    ''' Pure sugar. Print to stdout with just yield '''

    def wrapper(*args):
        for f in func(*args):
            print(f)

    return wrapper