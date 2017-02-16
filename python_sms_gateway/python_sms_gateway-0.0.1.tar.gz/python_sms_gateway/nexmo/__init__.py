__author__ = 'muhilvarnan.v'

import urllib
import urllib2
import json

class NexmoConnector(object):
    """
    Nexmo Connector class
    """

    def __init__(self, api_key, api_secret, sender="NEXMO"):
        """
        connector constructor
        :return:
        """
        self.url = "https://rest.nexmo.com/sms/json?"
        self.config = {
            'api_key': api_key,
            'api_secret': api_secret,
            'from': sender

        }

    def send(self, to, text):
        """
        send text message
        :param to:
        :param text:
        :return:
        """
        try:
            self.config['to'] = to
            self.config['text'] = text
            request = urllib2.Request(self.url+urllib.urlencode(self.config))
            request.add_header('Accept', 'application/json')
            response = urllib2.urlopen(request)
            if response.code == 200:
                data = json.loads(response.read())
                messages = data.get("messages", [])
                for message in messages:
                    if message.get("status")==0:
                        return {
                            "status":"success",
                            "response":data
                        }
                return {
                    "status":"failure",
                    "response":data
                }
            else:
                return {
                    "status":"error",
                    "response":response.read()
                }
        except Exception, e:
            return {
                "status":"error",
                "response":e
            }