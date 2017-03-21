from unittest import TestCase
from Core.command import Command
from Core.engine import CommandEngine
from Core.receiver import Receiver
from Core.recording import ReceiverRecording
import engine_tests_data


class EngineFixture(TestCase):
    
    def setUp(self):
        self._subscriber = ReceiverRecording()
          

    def test_execute(self):
        command = engine_tests_data.MyTestCommand()
        receiver = engine_tests_data.MyTestHandler()
        self._subscriber.record(engine_tests_data.MyTestCommand, lambda:receiver)
        self._command_engine = CommandEngine(self._subscriber)
        self._command_engine.process(command)
        self.assertEqual(receiver._mvalue, "modified value")
    
    def test_executeWithLogging(self):
        command = engine_tests_data.MyTestCommand()
        receiverLog = engine_tests_data.MyTestHandlerWithLog()
        self._subscriber.record(engine_tests_data.MyTestCommand, lambda:receiverLog)
        self._command_engine = CommandEngine(self._subscriber)
        self._command_engine.process(command)
        self.assertEqual(receiverLog._mvalue, "modified log value")

