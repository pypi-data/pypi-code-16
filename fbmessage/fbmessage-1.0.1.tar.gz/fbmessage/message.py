"""
Facebook Message API Implement
"""
from fbmessage.constants import GRAPH_API
import requests
import json


class Message(object):
    def __init__(self, access_token, valid_token):
        self.access_token = access_token
        self.valid_token = valid_token

    def send(self, recipient_id, text):
        url = GRAPH_API + '?access_token=' + self.access_token
        header = {'Content-Type': 'application/json'}
        payload = {'recipient': {'id': recipient_id}, 'message': {'text': text}}

        result = requests.post(url, data=json.dumps(payload), headers=header)
        return result
