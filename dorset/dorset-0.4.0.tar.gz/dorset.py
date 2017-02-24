# Copyright 2017 The Johns Hopkins University Applied Physics Laboratory LLC
# All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import json
from enum import Enum, IntEnum

"""
Dorset agent client library
~~~~~~~~~~~~~~~~~~~~~~~~~~~

This Dorset library handles the encoding and decoding of requests and
responses from a Dorset application. This supports the creation of
remote agents written in Python. Use this library with a python framework
for RESTful APIs like Flask, Bottle, or Django.

The web framework will handle HTTP requests and response and this Dorset
library will decode the request as an AgentRequest object and will encode
an AgentResponse.

With Flask, this will look like::

   app = Flask("dorset_hello")

   # required endpoint for the application to test if the agent is alive
   @app.route('/ping', methods=['GET'])
   def ping():
       return json.dumps("pong")

   # primary endpoint
   @app.route('/request', methods=['POST'])
   def process():
       agent_request = Dorset.decode_request(request.data)

       print(agent_request.text)

       return Dorset.encode_response(text="hello, world!")

"""


class Dorset(object):
    @staticmethod
    def decode_request(text):
        """Decodes JSON text into an AgentRequest

        :param text: JSON text sent from Dorset application
        :returns: AgentRequest object
        """
        obj = json.loads(text)
        request = AgentRequest(obj)
        return request

    @staticmethod
    def encode_response(type=None, text=None, status=None, payload=None):
        """Encodes a response as JSON text

        :param type: (optional) ResponseType instance
        :param text: (optional) Text of the response
        :param status: (optional) ResponseStatus instance
        :param payload: (optional) payload data as string
        :returns: AgentRequest object

        Usage::
          # simple response
          response = Dorset.encode_response(text="Lisbon is the capital of Portugal")

          # complex response
          response = Dorset.encode_response(type=ResponseType.JSON, text="Here is your chart", payload="json here")

          # simple error
          response = Dorset.encode_response(status=ResponseStatus(ResponseCode.AGENT_DID_NOT_KNOW_ANSWER))

          # custom error message
          status = ResponseStatus(ResponseCode.AGENT_INTERNAL_ERROR, "Cannot reach database.")
          response = Dorset.encode_response(status=status)
        """

        # text only
        if text is not None and type is None and status is None and payload is None:
            status = ResponseStatus.create_success()
            response = AgentResponse(ResponseType.TEXT, text, status)
        # status code only
        elif text is None and status is not None:
            response = AgentResponse(ResponseType.ERROR, None, status)
        # type, text and optional payload (no status)
        elif type is not None and text is not None:
            if status is None:
                status = ResponseStatus.create_success()
            response = AgentResponse(type, text, status, payload)
        # not supported combinations (payload only, payload and type only, etc)
        else:
            raise ValueError("Invalid combination of arguments")

        return json.dumps(response, cls=AgentResponseEncoder)


class User(object):
    ID = 'Dorset-id'
    USERNAME = 'Dorset-userName'
    FIRSTNAME = 'Dorset-firstName'
    LASTNAME = 'Dorset-lastName'
    LOCATION = 'Dorset-location'
    EMAIL = 'Dorset-email'
    DOB = 'Dorset-dob'

    def __init__(self, info=None):
        if info is None:
            self.info = {}
        else:
            self.info = info

    @property
    def id(self):
        return self.get(self.ID)

    @property
    def username(self):
        return self.get(self.USERNAME)

    @property
    def first_name(self):
        return self.get(self.FIRSTNAME)

    @property
    def last_name(self):
        return self.get(self.LASTNAME)

    @property
    def location(self):
        return self.get(self.LOCATION)

    @property
    def email(self):
        return self.get(self.EMAIL)

    @property
    def dob(self):
        return self.get(self.DOB)

    def get(self, key):
        try:
            return self.info[key]
        except KeyError:
            return None


class AgentRequest(object):
    def __init__(self, data):
        try:
            self.text = data['text']
        except KeyError:
            raise DorsetException("Invalid json. Missing key 'text")
        if 'user' in data:
            try:
                self.user = User(data['user']['userInformation'])
            except KeyError:
                raise DorsetException("Invalid json. Missing key 'userInformation")
        else:
            self.user = None


class ResponseCode(IntEnum):
    SUCCESS = 0
    INTERNAL_ERROR = 100
    NO_AVAILABLE_AGENT = 101
    NO_RESPONSE_FROM_AGENT = 102
    INVALID_RESPONSE_FROM_AGENT = 103
    AGENT_DID_NOT_UNDERSTAND_REQUEST = 200
    AGENT_DID_NOT_KNOW_ANSWER = 201
    AGENT_CANNOT_COMPLETE_ACTION = 202
    AGENT_INTERNAL_ERROR = 203


class ResponseStatus(object):
    messages = {
        ResponseCode.SUCCESS: 'Success',
        ResponseCode.INTERNAL_ERROR: 'Something failed with this request.',
        ResponseCode.NO_AVAILABLE_AGENT: 'No agent was available to handle this request.',
        ResponseCode.NO_RESPONSE_FROM_AGENT: 'The agent did not provide a response.',
        ResponseCode.INVALID_RESPONSE_FROM_AGENT: 'An error occurred getting response from agent.',
        ResponseCode.AGENT_DID_NOT_UNDERSTAND_REQUEST: 'The agent did not understand the request.',
        ResponseCode.AGENT_DID_NOT_KNOW_ANSWER: 'The agent did not know the answer.',
        ResponseCode.AGENT_CANNOT_COMPLETE_ACTION: 'The agent could not complete the requested action.',
        ResponseCode.AGENT_INTERNAL_ERROR: 'Something failed when handling this request.',
    }

    @classmethod
    def get_message(cls, code):
        return cls.messages[code]

    def __init__(self, code, message=None):
        self.code = code
        if message is None:
            self.message = ResponseStatus.get_message(code)
        else:
            self.message = message

    @staticmethod
    def create_success():
        return ResponseStatus(ResponseCode.SUCCESS)


class ResponseType(Enum):
    ERROR = 'error'
    TEXT = 'text'
    IMAGE_EMBED = 'image_embed'
    IMAGE_URL = 'image_url'
    JSON = 'json'


class AgentResponse(object):
    def __init__(self, response_type, text, status, payload=None):
        self.type = response_type
        self.text = text
        self.status = status
        self.payload = payload


class AgentResponseEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, AgentResponse):
            return {'type': obj.type, 'text': obj.text, 'status': obj.status, 'payload': obj.payload}
        if isinstance(obj, ResponseType):
            return obj.value
        if isinstance(obj, ResponseStatus):
            return {'code': int(obj.code), 'message': obj.message}
        return json.JSONEncoder.default(self, obj)


class DorsetException(Exception):
    """An error with encoding or decoding Dorset data"""


