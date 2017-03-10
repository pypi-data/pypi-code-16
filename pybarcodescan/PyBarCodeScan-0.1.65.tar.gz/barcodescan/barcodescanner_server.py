import logging
from flask import Flask
from flask import render_template
from flask import make_response
from flask import request
import os.path
from flask_sse import sse
import json
import redis
from barcodescan.WorkerDao import WorkerDao
from barcodescan.ScannedDataService import ScannedDataService
from barcodescan.Config import Config
from barcodescan.Push_client import Push_client


home_dir=os.environ['HOME']

app = Flask(__name__)
app.config["REDIS_URL"] = "redis://localhost"
app.register_blueprint(sse, url_prefix='/stream')

logging.basicConfig(level=logging.DEBUG)

dao = WorkerDao(redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True))
config = Config(home_dir + "/.barcodescanner.cfg")
service = ScannedDataService(dao, Push_client(config.server_push_url()))


@app.route("/", methods=['GET'])
def index():
  worker = service.get_worker()

  return render_template('index.html', sse_enabled= not app.debug, event_type="scans", worker_id=worker["key"], employee=worker.get("employee", "-"),
                         stage=worker.get("stage", "-"), jobs=worker.get("jobs", []))


@app.route("/", methods=['PUT'])
def put_data():
  last_scan = request.get_json()["data"]
  app.logger.debug("last scan: {}".format(last_scan))

  worker = service.put_scanned_data(last_scan)

  message = json.dumps({"message": worker})
  sse.publish(message, type='scans')
  return make_response("OK", 200)


if __name__ == "__main__":
  app.run(debug=True, port=8000)
