
import os, re, sys, logging
import sass                 # pip install libsass
from unum import Unum       # pip install unum
from bl.dict import Dict    # ordered dict with string keys
from bl.string import String
from bl.text import Text

LOG = logging.getLogger(__file__)

Unum.UNIT_FORMAT = "%s"
Unum.UNIT_INDENT = ""
Unum.VALUE_FORMAT = "%s"

pt = Unum.unit('pt')
px = Unum.unit('px', 0.75*pt)
em = Unum.unit('em', 12.*pt)
en = Unum.unit('en', 6.*pt)
inch = Unum.unit('in', 72.*pt)
pi = Unum.unit('pi', 12.*pt)
percent = Unum.unit('%', 0.01*em)
    
class Styles(Dict):
    pass
    # def keys(self):
    #     """Sort the keys: Alphabetical, except if a rule @extend a base rule, the base rule is earlier."""
    #     alpha_keys = Dict(**self).keys()    # Dict.keys() does alphabetical sort
    #     sorted_keys = []
    #     while len(alpha_keys) > 0:
    #         key = alpha_keys[0]
    #         style = self[key]
    #         while style.get('@extend') is not None:
    #             next_key = style.get('@extend').strip(' ;')
    #             if next_key in sorted_keys: break
    #             key = next_key
    #             style = self[key]
    #         sorted_keys.append(key)
    #         _ = alpha_keys.pop(alpha_keys.index(key))
    #     return sorted_keys

class SCSS(Text):
    # the style rules are keys in the "styles" dict. This is limiting, but it works --  
    # it happens to result in things being ordered correctly (with @-rules first), and 
    # it allows us to effectively query and manipulate the contents of the stylesheet at any time.

    def __init__(self, **args):
        # TODO: add parsing of text input into self.styles
        Text.__init__(self, **args)
        self.text = None
        if self.styles is None:
            self.styles = Styles()

    def write(self, fn=None):
        Text.write(self, fn=fn, text=self.render_styles())

    def render_css(self, fn=None, text=None):
        """output css using the Sass processor"""
        from bf.css import CSS
        fn = fn or os.path.splitext(self.fn)[0]+'.css'
        if not os.path.exists(os.path.dirname(fn)):
            os.makedirs(os.path.dirname(fn))
        os.chdir(os.path.dirname(fn))               # needed in order for scss to relative @import
        c = CSS(fn=fn, text='')
        t = text or self.render(self.styles)
        c.text = sass.compile(t)
        return c
    
    def render_styles(self, margin="", indent="\t"):
        return self.render(self.styles)

    @classmethod    
    def render(c, styles, margin="", indent="\t"):
        """output scss text from styles. 
        margin is what to put at the beginning of every line in the output.
        indent is how much to indent indented lines (such as inside braces)."""

        def render_dict(d):
            return ('{\n' 
                    + c.render(styles[k], 
                        margin=margin+indent,   # add indent to margin
                        indent=indent) 
                    + '}')

        # render the scss text
        s = ""
        for k in styles.keys():
            LOG.debug(margin, k, styles[k])
            s += margin + k + ' '
            if type(styles[k]) in [str, String]:
                s += styles[k] + ';'
            elif type(styles[k])==Unum:
                s += str(styles[k]) + ';'
            elif type(styles[k]) in [dict, Dict]:
                s += render_dict(styles[k])
            elif type(styles[k]) in [tuple, list]:
                for i in styles[k]:
                    if type(i) in [str, String]:
                        s += i + ' '
                    if type(i) == bytes:
                        s += str(i, 'utf-8') + ' '
                    elif type(i) in [dict, Dict]:
                        s += render_dict(i)
            else:
                LOG.debug(margin, type(styles[k]), k, styles[k], file=sys.stderr)
                s += ';'
            s += '\n'
        return s
