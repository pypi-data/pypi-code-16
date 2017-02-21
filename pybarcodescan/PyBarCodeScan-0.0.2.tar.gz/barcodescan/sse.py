import logging
from flask import Flask
from flask import render_template
from flask import make_response
from flask import request
from flask_sse import sse
import os
import json

print("os.path.dirname(__file__): {}".format(os.path.dirname(__file__)))
print("os.path.abspath(os.path.dirname(__file__)): {}".format(os.path.abspath(os.path.dirname(__file__))))
print("os.path.dirname(os.path.abspath(os.path.dirname(__file__))): {}".format(os.path.dirname(os.path.abspath(os.path.dirname(__file__)))))
print("os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__)))): {}".format((os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__)))))))
template_dir = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
template_dir = os.path.join(template_dir, 'templates')
print("template_dir: {}".format(template_dir))
app = Flask(__name__, template_folder=template_dir)
app.config["REDIS_URL"] = "redis://localhost"
logging.basicConfig(level=logging.DEBUG)
app.register_blueprint(sse, url_prefix='/stream')


@app.route("/", methods=['GET'])
def index():
  return render_template('index.html', event_type="scans")


@app.route("/", methods=['PUT'])
def put_data():
  data_as_json = request.get_json()
  message = json.dumps({"message": data_as_json["data"]})
  sse.publish(message, type='scans')
  return make_response("OK", 200)
