import requests
import json


class OneAlert(object):

    def call(self, exceptions):
        for exception in exceptions:
            url = 'http://api.110monitor.com/alert/api/event'
            payload = json.dumps({
                'app': 'bcc67cab-afab-8259-6f86-42402abc52ab',
                'eventId': exception['case'],
                'eventType': 'trigger',
                'alarmName': exception['message'],
                'entityName': exception['case'] + '-name',
                'entityId': exception['case'] + '-id',
                'priority': 1,
                'alarmContent': exception
            })
            requests.post(url, payload)
