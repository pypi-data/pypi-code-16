from typing import Optional
from Core.command import Command
from Core.recording import ReceiverRecording
from Core.exceptions import EngineException


class CommandEngine(object):

    def __init__(self, receiver_factory:Optional[ReceiverRecording]=None):
        self._receiver_factory = receiver_factory
    
    def process(self, my_command:Command) -> None:
       if not self._receiver_factory:
           raise EngineException("no factory found")
       receiver = self._receiver_factory.resolve(my_command)
       receiver_object = receiver()
       receiver_object.execute(my_command)
        
    

    

