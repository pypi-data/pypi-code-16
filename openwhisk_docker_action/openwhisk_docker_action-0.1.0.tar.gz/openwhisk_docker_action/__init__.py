import flask
import json

class Action(flask.Flask):

    def __init__(self, name='My Openwhisk Action'):
        flask.Flask.__init__(self,name)
        self.add_url_rule('/init', 'init', self.initroute, methods=['POST'])
        self.add_url_rule('/run', 'run', self.runner, methods=['POST'])
        self._func = None

    def initroute(self):
        return flask.Response('{}',
                              status=200,
                              mimetype='application/json')

    def json_dict(self, res):
        if isinstance(res, dict):
            return json.dumps(res)
        else:
            return json.dumps({'results': res})
        
    def runner(self):
        full_params = flask.request.get_json()
        if self._func:
            params = {}
            if full_params:
                params = full_params
            print(full_params)
            results = self._func(params)
            return flask.Response(response=self.json_dict(results),
                                  status=200,
                                  mimetype='application/json')
        else:
            resp_string = "{'error':'no function to run'}"
            return flask.Response(response=resp_string,
                                  status=405,
                                  mimetype='application/json')

    def main(self,func):
        self._func = func
        self.run(host='0.0.0.0')
