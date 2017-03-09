import os
import requests
import json

from oslo_config import cfg
CONF = cfg.CONF

notify_sms_url = os.getenv('NOTIFY_SMS_URL')
notify_sms_key = os.getenv('NOTIFY_SMS_KEY')
notify_sms_secret = os.getenv('NOTIFY_SMS_SECRET')
notify_sms_mobiles = os.getenv('NOTIFY_SMS_MOBILE')

region_name = os.getenv('REGION_NAME')


class SmsAlert(object):

    def __init__(self):
        self.endpoint = CONF.endpoint
        self.access_key = CONF.key

    def call(self, exceptions):
        if (not notify_sms_url or
           not notify_sms_key or
           not notify_sms_secret or
           not notify_sms_mobiles or
           not region_name):
            return

        for ex in exceptions:
            text = []
            text.append('region: %s' % region_name)
            text.append('endpoint: %s' % self.endpoint)
            text.append('access_key: %s' % self.access_key)
            text.append('case: %s' % ex['case'])
            text.append('exception: %s' % ex['message'])
            text = '\n'.join(text)

            payload = {
                'content': text,
                'tos': notify_sms_mobiles
            }

            headers = {
                'X-Le-Key': notify_sms_key,
                'X-Le-Secret': notify_sms_secret,
            }

            try:
                requests.post(notify_sms_url,
                              data=json.dumps(payload),
                              headers=headers)
            except:
                pass
