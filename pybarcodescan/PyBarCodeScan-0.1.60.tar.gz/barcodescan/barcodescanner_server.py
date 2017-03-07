import logging
from flask import Flask
from flask import render_template
from flask import make_response
from flask import request
import os.path
from flask_sse import sse
import json
import uuid
import redis
from barcodescan.WorkerDao import WorkerDao
from barcodescan.ScannedDataService import ScannedDataService

def generate_or_get_unique_id(file_path):
  if not os.path.isfile(file_path):
    with open(file_path, "w") as f:
      f.write(str(uuid.uuid4()))
  with open(file_path, "r") as f:
    return f.readlines()[0]


app = Flask(__name__)
app.config["REDIS_URL"] = "redis://localhost"
logging.basicConfig(level=logging.DEBUG)
r = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
dao = WorkerDao(r)

home_dir=os.environ['HOME']
sse_enabled = True
if os.environ.get('FLASK_DEBUG') == "1":
  sse_enabled = False

service = ScannedDataService(generate_or_get_unique_id(home_dir + "/.barcodescanner"), dao)

app.register_blueprint(sse, url_prefix='/stream')


@app.route("/", methods=['GET'])
def index():
  worker = service.get_worker()
  return render_template('index.html', sse_enabled= sse_enabled, event_type="scans", worker_id=worker["key"], employee=worker.get("employee", "-"),
                         stage=worker.get("stage", "-"), jobs=worker.get("jobs", []))


@app.route("/", methods=['PUT'])
def put_data():
  last_scan = request.get_json()["data"]
  app.logger.debug("last scan: {}".format(last_scan))

  worker = service.put_scanned_data(last_scan)

  message = json.dumps({"message": worker})
  sse.publish(message, type='scans')
  return make_response("OK", 200)
