import logging
from Core.command import Command
from Core.receiver import Receiver
from Core.request import Request
from Core.receiver_log import receiver_log, OutputType

class MyTestHandler(Receiver):
    def __init__(self):
        self._mvalue = "base value"
    
    
    def execute(self, request:Request):
        self._mvalue = "modified value"
        

class MyTestHandlerWithLog(Receiver):
    def __init__(self):
        self._mvalue = "base log value"
    
    @receiver_log(logging.DEBUG, OutputType.file_output)
    def execute(self, request:Request):
        self._mvalue = "modified log value"


class MyTestCommand(Command):
    def __init__(self):
        super().__init__()
    
    
