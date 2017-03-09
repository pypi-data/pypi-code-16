import json
import operator

import attr

from twisted.internet import task

import klein

def _get_numbers(request):
    body = json.loads(request.content.read().decode('utf-8'))
    return map(int, body)

def _send_number(request, dfrd):
    request.setHeader('Content-Type', 'application/json')
    dfrd.addCallback(json.dumps)
    return dfrd

@attr.s
class Operations(object):

    app = klein.Klein()
    clock = attr.ib()

    @app.route('/multiply')
    def multiply(self, request):
        a, b = _get_numbers(request)
        res = task.deferLater(self.clock, 5, operator.mul, a, b)
        return _send_number(request, res)

    @app.route('/negate')
    def negate(self, request):
        a, = _get_numbers(request)
        res = task.deferLater(self.clock, 3, operator.neg, a)
        return _send_number(request, res)
