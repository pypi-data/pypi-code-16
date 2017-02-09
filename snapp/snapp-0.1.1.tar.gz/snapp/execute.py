from ioc import SingleObjectContainer
import sys
from module import Module

class ModuleExecuter():
    """
    Simple executer which creates an ioc container and calls "start".
    """
    kwargs = None
    args = None
    exit_code = 0

    def __init__(self):
        self.entry()

    def register(self, module):
        if self.__ioc__ is None:
            self.__ioc__ = SingleObjectContainer(obj_type = Module)
        module.__ioc__ = self.__ioc__
        self.__ioc__.register(module.id, module)

    #Entry point for the executer
    def entry(self):
        self.start()
        sys.exit(exit_code)
        
