# coding: utf-8
from os import path
import base64
from datetime import datetime
import uuid
import simplejson as json


class BasicMessage(object):
    """ Basic unit of communication that will be used for remote communications, you need at least
    specify the sender, receiver and a message body (command, error, status, etc)::

        >>> message = messagev.BasicMessage()
        >>> message.sender_node_id = 'me01'
        >>> message.receiver_node_id = 'you01'
        >>> res = message.build_message()

    The :func:`~deployv.base.messagev.BasicMessage.build_message` method generates the proper
    message according to the defines schema for the communication (check test_messagev.py
    in the tests folder)

    """

    def __init__(self, message=None):
        envelope = {
            'version': '0.1',
            'message_id': str(uuid.uuid1()),
            'deploy_id': None,
            'orchest_pipe_id': None,
            'sender_node_id': None,
            'receiver_node_id': None,
            'timestamp': None,
            'response_to': None,
            'message_body': dict(),
            'model': None
        }
        self.__dict__ = envelope.copy()
        self._envelope = envelope.copy()
        self._files = list()
        self._message_types = ['error', 'result', 'parameters']
        if message is None:
            self._original_message = None
        elif isinstance(message, str):
            self._original_message = json.loads(message)
        elif isinstance(message, dict):
            self._original_message = message.copy()
        else:
            raise TypeError('Message is in a unsupported type {}'.format(type(message)))
        if self._original_message is not None:
            for key in envelope:
                setattr(self, key, self._original_message[key])

    @property
    def original_message(self):
        return self._original_message

    def attach_file(self, file_name, mime_type=None):
        assert path.isfile(file_name)
        self._files.append((file_name, mime_type))

    def set_message_body(self, message_body, message_type):
        """ Define the message body to be send

        :param message_body: Message body according to the documentation
        :param message_type: Error, ack, response or parameters
        :return: None
        """
        if message_type not in self._message_types:
            raise ValueError('Message type must be one of: {}'.format(str(self._message_types)))
        self.message_body = message_body

    def set_command(self, module_command, parameters):
        """ Helper method to create the message for a command

        :param module_command: Execute the command from the specified module.
            Must be in the format module.command
        :param parameters: The parameters that will be passed to the command in a dict
        :return: None
        """
        assert len(module_command.split('.')) == 2
        assert isinstance(parameters, dict)
        res = {
            'module': module_command.split('.')[0],
            'command': module_command.split('.')[1],
            'parameters': parameters
        }
        self.message_body = res

    def build_message(self):
        """ Builds the message with the provided properties in the class and according to the type

        :return: The formatted message in a dict
        """
        res = dict()
        attachments = list()
        for key in self._envelope:
            res.update({key: getattr(self, key)})
        res.update({
            'timestamp': datetime.utcnow().isoformat()})
        for fname in self._files:
            with open(fname(0)) as fname_descriptor:
                coded_file = base64.b64encode(fname_descriptor.read())
            attachments.append({
                'file_name': path.basename(fname(0)),
                'file': coded_file,
                'type': fname(1)
            })
        if self._original_message:
            res.update({
                'receiver_node_id': self._original_message.get('sender_node_id'),
                'sender_node_id':  self._original_message.get('receiver_node_id'),
                'model': self._original_message.get('model')
            })
        if res.get('message_body').get('error', False) and len(attachments):
            res.get('message_body').get('error').update({'attachments': attachments})
        elif res.get('message_body').get('result', False) and len(attachments):
            res.get('message_body').get('result').update({'attachments': attachments})
        return res

    def get_ack_message(self, send_to=None):
        """ When a message is provided in the constructor this method generates an ack response
        with the proper parameters

        :param send_to: message route if none is provided will use default
                        passed to the class constructor
        :return: The ack message
        """
        if self._original_message is None:
            res = self.build_message()
        else:
            res = self._original_message.copy()
        res.update({
            'receiver_node_id': res.get('receiver_node_id'),
            'sender_node_id':  res.get('sender_node_id') if send_to is None else send_to,
            'model': res.get('model'),
            'timestamp': self.timestamp,
            'response_to': res.get('message_id'),
            'message_id': str(uuid.uuid1()),
            'message_body': {
                'module': res.get('message_body').get('module'),
                'command': res.get('message_body').get('command'),
                'ack': {
                    'message': 'Message received'
                }
            }
        })
        return BasicMessage(message=res)

    def get_message_str(self):
        """ A simple helper method that returns the message as a str but being sure that it will
        be safe for rabbitmq

        :return: The string representing the message
        """
        return json.dumps(self.build_message(),
                          ensure_ascii=True,
                          check_circular=True,
                          encoding='utf-8')

    def __repr__(self):
        return self.get_message_str()
