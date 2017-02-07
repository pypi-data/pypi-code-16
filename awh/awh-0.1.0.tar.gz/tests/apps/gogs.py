import json

from awh import Awh
from awh.operate import require, jsonpath

app = Awh()
secret_key = 'blahs'


@app.validator('gogs_push')
def validate_gogs_push(request):
    payload = request.get_data(as_text=True)
    j = json.loads(payload)

    require(jsonpath(j, 'secret')[0].value == secret_key,
            'incorrect key')
    require(jsonpath(j, 'repository.full_name')[0].value == 'gogs/gogs',
            'incorrect repository')
    require(jsonpath(j, 'pusher.username')[0].value == 'unknwon',
            'incorrect pusher')
    return True


@app.executor('gogs_push')
def execute_gogs_push(request):
    pass
