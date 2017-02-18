from __future__ import print_function

import tellurium as te
set_model = te.__set_model
from roadrunner import RoadRunner

# http://stackoverflow.com/questions/28703626/ipython-change-input-cell-syntax-highlighting-logic-for-entire-session
import IPython
#js = "IPython.CodeCell.config_defaults.highlight_modes['magic_fortran'] = {'reg':[/^%%fortran/]};"
#IPython.core.display.display_javascript(js, raw=True)

from IPython.core.magic import (Magics, magics_class, line_magic,
                                cell_magic, line_cell_magic)

# The class MUST call this class decorator at creation time
@magics_class
class MyMagics(Magics):
    def checkAntimonyReturnCode(self, code):
        "Negative return code (usu. -1) from Antimony signifies error"
        return (code < 0)

    @cell_magic
    def crn(self, line, cell):
        "Defines a chemical reaction network (CRN) in Antimony syntax"
        import antimony as sb
        # try to load the Antimony code`
        code = sb.loadAntimonyString(cell)

        # if errors, bail
        if self.checkAntimonyReturnCode(code):
            errors = sb.getLastError()
            raise RuntimeError('Errors encountered when trying to load model:\n{}'.format(errors))
        module = sb.getMainModuleName()
        sbml_str = sb.getSBMLString(module)

        # override name?
        if line:
            if module == '__main':
                module = line
            else:
                raise RuntimeError('Conflicting names for model: {} vs {}. Please specify one or the other.'.format(module, line))

        set_model(module, RoadRunner(sbml_str))
        print("Success: Model can be accessed via variable {}".format(module))
        if module == '__main':
            print('Consider enclosing your code in a model definition to name your model:\nmodel name_of_your_model()\n  ...\nend')

        # add RoadRunner instance to global namespace
        import sys
        sys.modules['builtins'].__dict__[module] = te.model(module)

ip = get_ipython()
ip.register_magics(MyMagics)
