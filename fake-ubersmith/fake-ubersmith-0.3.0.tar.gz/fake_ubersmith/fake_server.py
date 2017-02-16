# Copyright 2017 Internap.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import requests
import threading

from flask import request, Flask


class FlaskServer(threading.Thread):
    def __init__(self, name, port=9124, *args, **kwargs):
        super(FlaskServer).__init__(*args, **kwargs)

        self.server = Flask(name)
        self.port = port

        self.server.add_url_rule('/__shutdown', view_func=shutdown)

    def run(self):
        self.server.run(host="0.0.0.0", port=self.port)

    def stop(self):
        requests.get('http://localhost:{0}/__shutdown'.format(self.port))


def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
