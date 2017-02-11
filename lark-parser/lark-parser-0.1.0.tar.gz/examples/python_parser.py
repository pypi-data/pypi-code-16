import os, os.path
from io import open

from lark import Lark
from lark.indenter import Indenter

__path__ = os.path.dirname(__file__)

class PythonIndenter(Indenter):
    NL_type = '_NEWLINE'
    OPEN_PAREN_types = ['__LPAR', '__LSQB', '__LBRACE']
    CLOSE_PAREN_types = ['__RPAR', '__RSQB', '__RBRACE']
    INDENT_type = '_INDENT'
    DEDENT_type = '_DEDENT'
    tab_len = 8

python_grammar_file = os.path.join(__path__, '../grammars/python2.g')
with open(python_grammar_file) as f:
    python_parser = Lark(f, parser='lalr', postlex=PythonIndenter(), start='file_input')


# print list(python_parser.lex('if True:\n  print "hello"\n'))
def test1():
    for fn in os.listdir(__path__):
        if fn.endswith('.py'):
            with open(os.path.join(__path__, fn)) as f:
                print(fn)
                text = f.read()
                print(python_parser.parse(text).pretty())
# print python_parser.parse('if True:\n  print "hello"\n')

def _read(fn, *args):
    kwargs = {'encoding': 'iso-8859-1'}
    with open(fn, *args, **kwargs) as f:
        return f.read()

def test2():
    import glob, sys, time
    if os.name == 'nt':
        if 'PyPy' in sys.version:
            path = os.path.join(sys.prefix, 'lib-python', sys.winver)
        else:
            path = os.path.join(sys.prefix, 'Lib')
    else:
        path = [x for x in sys.path if x.endswith('%s.%s' % sys.version_info[:2])][0]

    start = time.time()
    files = glob.glob(path+'/*.py')
    for f in files:
        print( f )
        try:
            print list(python_parser.lex(_read(os.path.join(path, f)) + '\n'))
            python_parser.parse(_read(os.path.join(path, f)) + '\n')
        except:
            print ('At %s' % f)
            raise

    end = time.time()
    print( "test_python_lib (%d files), time: %s secs"%(len(files), end-start) )


test2()
