import os
import requests
import json

from oslo_config import cfg
CONF = cfg.CONF

slack_hook_url = os.getenv('PLATO_CAT_SLACK_HOOK')
region_name = os.getenv('REGION_NAME')


class SlackAlert(object):

    def __init__(self):
        self.endpoint = CONF.endpoint
        self.access_key = CONF.key

    def call(self, exceptions):
        if not slack_hook_url or not region_name:
            return

        for ex in exceptions:
            text = []
            text.append('region: %s' % region_name)
            text.append('endpoint: %s' % self.endpoint)
            text.append('access_key: %s' % self.access_key)
            text.append('case: %s' % ex['case'])
            text.append('exception: %s' % ex['message'])
            text.append('traceback: %s' % ex['traceback'])
            text = '\n'.join(text)

            payload = {'text': text}

            try:
                requests.post(slack_hook_url, data=json.dumps(payload))
            except:
                pass

    def report(self, title, is_pass, stat):
        if not slack_hook_url:
            return

        text = []
        text.append('endpoint: %s' % self.endpoint)
        text.append('access_key: %s' % self.access_key)
        text.append(title)
        text.append('Pass: %s' % is_pass)

        text.append('%s: %s' % (k, v) for k, v in stat.items())

        text = '\n'.join(text)

        payload = {'text': text}

        try:
            requests.post(slack_hook_url, data=json.dumps(payload))
        except:
            pass
