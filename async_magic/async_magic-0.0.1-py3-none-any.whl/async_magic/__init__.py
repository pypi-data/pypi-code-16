""" Define an async_magic for IPython that fake the async keyword at top level
scope.
"""

version_info = (0,0,1)
__version__ = '.'.join([str(x) for x in version_info])


from IPython.core.magic import magics_class, Magics, line_magic

@magics_class
class AAWait(Magics):

    def __init__(self, shell):
        import asyncio
        super().__init__(shell)
        self.loop = asyncio.get_event_loop()

    @line_magic
    def loop(self, param:str):
        self.loop = self.shell.user_ns[param.strip()]

    @line_magic
    def await(self, param:str):
        self.shell.user_ns.setdefault('__loop', self.loop)
        self.shell.run_cell("""
import asyncio
__res = __loop.run_until_complete(%s)
        """ % param)
        return self.shell.user_ns.get('__res')

def load_ipython_extension(shell):
    shell.register_magics(AAWait)

