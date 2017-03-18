"""
Facebook Message API Implement
"""
from fbmessage.constants import GRAPH_API
import requests
import json


class Message(object):
    def __init__(self, verify_token, page_access_token):
        self.verify_token = verify_token
        self.page_access_token = page_access_token

    def send_text_message(self, recipient_id, text):
        url = GRAPH_API + '?access_token=' + self.page_access_token
        header = {'Content-Type': 'application/json'}
        payload = {'recipient': {'id': recipient_id}, 'message': {'text': text}}

        result = requests.post(url, data=json.dumps(payload), headers=header)
        return result
