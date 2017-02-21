import os
import requests
from flask import Flask, request
app = Flask(__name__)

PROXIES = {
    'http': os.environ['HTTP_PROXY'],
    'https': os.environ['HTTPS_PROXY']
}

SLACK_BASE = 'https://hooks.slack.com/services'
TOKEN = os.environ['SLACK_TOKEN']


@app.route('/relay', methods=['POST'])
def webhook_relay():

    print request.json

    if forward_request(payload=request.json):
        return "OK\n"


def forward_request(payload):

    url = SLACK_BASE + TOKEN

    r = requests.post(url,
                      proxies=PROXIES,
                      json=payload,
                      headers={'Content-Type': 'application/json'})

    if r.status_code == requests.codes.ok:
        return True
    else:
        return False


def start():
    app.run()
