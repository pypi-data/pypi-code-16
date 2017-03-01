"""
A simple IPython extension which changes the representation of bytes to
look like bytes and not text.
"""


version_info = (0,0,2)
__version__ = '.'.join([str(x) for x in version_info])


ellide = lambda s: s if (len(s) < 75) else  s[0:50]+'...'+s[-16:]
def _print_bytestr(arg, p, cycle):
    p.text('<bytes '+ellide(repr(arg))+' at {}>'.format(hex(id(arg))))       




def enable():
    text_formatter = get_ipython().display_formatter.formatters['text/plain']
    text_formatter.for_type(bytes, _print_bytestr)
