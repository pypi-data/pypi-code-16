#!/usr/bin/python
# -*- coding: utf8 -*-

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

import sys
import time
from flask import Flask, request, jsonify
from .geofluent import GeoFluent

app = Flask(__name__)


@app.route("/", methods=["POST"])
def serve():
    data = request.get_data()
    charset = request.mimetype_params.get('charset') or 'UTF-8'
    data = data.decode(charset, 'replace')
    source = request.args.get('source')
    target = request.args.get('target')
    print(data)
    translation = app.gf.translate(data, source, target)
    print(translation)
    response = {
        "data": data,
        "translation": {
            "text": translation,
            "source": source,
            "target": target
        },
        "timestamp": time.time()
    }
    return jsonify(response)


@app.route("/", methods=["HEAD"])
def head():
    return ""


if __name__ == "__main__":
    app.gf = GeoFluent(key=sys.argv[1], secret=sys.argv[2])
    port = int(sys.argv[3]) if len(sys.argv) > 3 else 5000
    app.run(host="0.0.0.0", port=port)
