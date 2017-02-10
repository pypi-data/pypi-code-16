from shaman.src.analyzers.abstract_stage import AbstractStage
from shaman.src.abstract_message import control_messages_invert_dict, MessageFormat

import json


class StdinReaderStage(AbstractStage):
    """
    Reads messages from a standard input.

    Input data:
            - str from stdin
        Output data:
            - url
            - owner
            - comment
            - parsed_json

    Using modules:
        - json (https://docs.python.org/2/library/json.html)
    """
    def init_stage(self):
        self.owner = self.config['owner']
        self.comment = self.config['comment']

    def do_stage(self, message):
        message.owner = self.owner
        message.comment = self.comment

        message.stdin_line = self.in_queue.get()
        message = self._process_input_line(message.stdin_line, message)

        try:
            if message.stdin_line[0]=='{':
                parsed_json = json.loads(message.stdin_line)
                for field in parsed_json:
                    message.__dict__[field] = parsed_json[field]
            else:
                message.url = message.stdin_line
        except ValueError as e:
            message.url = message.stdin_line

        return message

    def _process_input_line(self, line, message):
        if line in control_messages_invert_dict:
            if control_messages_invert_dict[line] == 'shutdown':
                message.format = MessageFormat.CONTROL
                message.control_message = 'shutdown'
        return message