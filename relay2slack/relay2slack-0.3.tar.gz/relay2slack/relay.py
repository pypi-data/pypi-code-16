import os
import sys
import requests
from flask import Flask, request
app = Flask(__name__)

try:
    http_proxy = os.environ['HTTP_PROXY']
    https_proxy = os.environ['HTTPS_PROXY']
    TOKEN = os.environ['SLACK_TOKEN']

except KeyError as e:
    print("Ensure the environment variable {} is set.".format(e.args[0]))
    sys.exit(1)

PROXIES = {
    'http': http_proxy,
    'https': https_proxy
}

SLACK_BASE = 'https://hooks.slack.com/services'


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
