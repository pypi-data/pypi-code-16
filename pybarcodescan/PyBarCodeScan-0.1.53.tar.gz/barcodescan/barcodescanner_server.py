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

def generate_or_get_unique_id(file_path):
  if not os.path.isfile(file_path):
    with open(file_path, "w") as f:
      f.write(str(uuid.uuid4()))
  with open(file_path, "r") as f:
    return f.readlines()[0]


app = Flask(__name__)
app.config["REDIS_URL"] = "redis://localhost"
home_dir=os.environ['HOME']
app.logger.info("HOME: {}".format(home_dir))
app.config["UUID"] = generate_or_get_unique_id(home_dir + "/.barcodescanner")
logging.basicConfig(level=logging.DEBUG)
r = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)


app.register_blueprint(sse, url_prefix='/stream')


@app.route("/", methods=['GET'])
def index():
  worker_id = app.config["UUID"]
  worker = r.hgetall(worker_id)
  if not worker:
    worker = {"id": worker_id}
    r.hmset(worker_id, worker)
  if not "jobs" in worker:
    jobs=[]
  else:
    jobs = worker["jobs"].split(",")

  if not "stage" in worker:
    stage="-"
  else:
    stage=worker["stage"]

  if not "employee" in worker:
    employee="-"
  else:
    employee=worker["employee"]


  return render_template('index.html', event_type="scans", worker_id=worker["id"], employee=employee,
                         stage=stage, jobs=jobs)


@app.route("/", methods=['PUT'])
def put_data():
  last_scan = request.get_json()["data"]
  app.logger.debug("last scan: {}".format(last_scan))
  worker_id = app.config["UUID"]
  worker = r.hgetall(worker_id)
  if not worker:
    worker = {"id": worker_id}
    r.hmset(worker_id, worker)

  splitted_str = last_scan.split('-')
  if splitted_str[0] == "mit":
    worker["employee"] = splitted_str[1]
  if splitted_str[0] == "platz":
    worker["stage"] = splitted_str[1]
  if splitted_str[0] == "a":
    other_jobs = []
    if "jobs" in worker:
      other_jobs=worker["jobs"].split(",")
    other_jobs.append(splitted_str[1])
    worker["jobs"]=",".join(set(other_jobs))
  r.hmset(worker_id, worker)

  message = json.dumps({"message": worker})
  sse.publish(message, type='scans')
  return make_response("OK", 200)
