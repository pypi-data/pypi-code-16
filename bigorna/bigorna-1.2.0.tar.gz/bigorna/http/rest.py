import logging

from flask import Blueprint, jsonify, send_file, Response, current_app, request
from os import path

api = Blueprint('api', __name__)
log = logging.getLogger(__name__)
NOT_FOUND = Response(status=404)


@api.route('/jobs/<string:job_type>', methods=['POST'])
def submit_job(job_type):
    params = request.get_json()
    log.info('Submit job request: %s - %s', job_type, params)
    job = current_app.bigorna.submit(job_type, params)
    return jsonify(job.as_dict()), 201


@api.route('/jobs')
def list_jobs():
    log.info('List job request')
    raw = current_app.bigorna.list_jobs()
    jobs = list(map(lambda j: j.as_dict(), raw))
    return jsonify(jobs), 200


@api.route('/jobs/<string:job_id>')
def get_job(job_id):
    log.info('Get job request: %s', job_id)
    job = current_app.bigorna.get_job(job_id)
    if job:
        resp = jsonify(job.as_dict()), 200
    else:
        resp = NOT_FOUND

    return resp


@api.route('/jobs/<string:job_id>/output')
def job_output(job_id):
    log.info('Get job output request: %s', job_id)
    job = current_app.bigorna.get_job(job_id)
    if job and path.isfile(job.output_file):
        resp = send_file(job.output_file, as_attachment=False)
    else:
        resp = NOT_FOUND

    return resp
