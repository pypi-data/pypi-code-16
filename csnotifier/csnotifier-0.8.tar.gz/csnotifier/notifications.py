import json
import requests
from django.conf import settings

PUSHWOOSH_APP_ID = getattr(settings, 'PUSHWOOSH_APP_ID', '')
PUSHWOOSH_AUTH_TOKEN = getattr(settings, 'PUSHWOOSH_AUTH_TOKEN', '')
PUSHWOOSH_URL = getattr(settings, 'PUSHWOOSH_URL', 'https://cp.pushwoosh.com/json/1.3/createMessage')
FIREBASE_API_KEY = getattr(settings, 'FIREBASE_API_KEY', '')
FIREBASE_URL = getattr(settings, 'FIREBASE_URL', '')

def _create__pushwoosh_message(devices, notification):
    message = {
        'request': {
            'application': PUSHWOOSH_APP_ID,
            'auth': PUSHWOOSH_AUTH_TOKEN,
            'notifications': [{
                'send_date': 'now',
                'content': notification.getTitle(),
                'data': notification.getExtra(),
                'devices' : devices
            }]
        }
    }
    return message

def _create__firebase_message(devices, notification):
    message = {
        'registration_ids': devices,
        'data': {
            'title': notification.getTitle(),
            'message': notification.getDesc(),
            'content': notification.getExtra()
        }
    }
    return message


def send_request(devices, notification):
    if PUSHWOOSH_APP_ID:
        headers = {'Content-Type': 'application/json'}
        payload = json.dumps(_create__pushwoosh_message(devices, notification))
        response = requests.post(PUSHWOOSH_URL, payload.encode('utf8'), headers=headers)
    else:
        headers = {
            'Authorization': 'key='+ FIREBASE_API_KEY,
            'Content-Type': 'application/json'
        }
        payload = json.dumps(_create__firebase_message(devices, notification))
        response = requests.post(FIREBASE_URL, payload.encode('utf8'), headers=headers)    

    if response and response.status_code == 200:
        return response.json()
    else:
        return {}


