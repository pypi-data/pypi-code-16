import hmac
import hashlib
import json

from awh import Awh
from awh.operate import require, digest_eq, jsonpath

app = Awh()
secret_key = 'foobar'


def hexdigest(key, payload):
    h = hmac.new(key.encode('utf-8'), payload, digestmod=hashlib.sha1)
    return h.hexdigest()


def signature(sig_header):
    if not sig_header:
        return
    type_, _, sha = sig_header.partition('=')
    if type_ == 'sha1' and sha:
        return sha
    return


@app.validator('github_push')
def validate_github_push(request):
    sig = signature(request.headers.get('HTTP_X_HUB_SIGNATURE'))
    require(digest_eq(sig, hexdigest(secret_key, request.get_data())),
            'bad signature')

    payload = request.get_data(as_text=True)
    j = json.loads(payload)

    require(jsonpath(j, 'ref')[0].value == 'refs/heads/master',
            'wrong branch')
    require(jsonpath(j, 'repository.full_name')[0].value == 'example_user/somerepo',
            'wrong repository')
    require(jsonpath(j, 'pusher.name')[0].value == 'example_user',
            'wrong pushing person')

    return True


@app.executor('github_push')
def execute_github_push(request):
    pass


@app.app
def myapp(request, response):
    pass
