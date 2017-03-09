import sys
import time


def get_resource(API, action, payload, result_set, max_length=400):
    """
    get max 400 length resources. that is 20 http requests round.
    """
    resources = []

    payload = payload or {}
    payload['limit'] = 20
    payload['offset'] = 0

    total = -1

    while True:
        payload['offset'] = len(resources)

        result = API.conn.call(action, payload)

        if total != result['total'] and total != -1:
            # total change. reset resources and start over.
            resources = []
            total = result['total']
            continue

        if total == -1:
            total = result['total']

        resources += result[result_set]

        if result['total'] <= len(resources):
            # have find all.
            break

        if len(resources) > max_length:
            # have reach max.
            break

    return resources


def wait_busy_resource(API, action, busy_payload, sleep, timeout=60*5):
    """
    describe busy resources, if total is not 0, means they are still busy,
    wait 4 seconds and try next time.
    """

    if timeout == 0:
        timeout = sys.maxint

    start = time.time()

    while True:
        result = API.conn.call(action, busy_payload)
        if result['total'] == 0:
            # no busy resource. good.
            break

        result.pop('total')
        result.pop('limit')
        result.pop('offset')

        id_key = result.keys()[0][0:-3] + 'Id'
        resources = result.values()[0]

        sleep(4)

        if time.time() - start > timeout:
            instance_status = dict((r[id_key], r['status']) for r in resources)
            raise Exception('wait_busy_resource timeout. '
                            'maybe job was not completely executed? '
                            'resources => status map: %s' % instance_status)


def post_resource(API, action, resources, ids_key):
    """
    post max 400 resources. that is 20 http requests round.
    """
    resources = resources[0:400]

    while resources:
        payload = {}
        payload[ids_key] = resources[:20]

        API.conn.call(action, payload)

        resources = resources[20:]


def wait_for_job(API, job_ids, sleep, timeout=60*5):
    """
    wait a job for at most 5 minutes.
    """
    if not job_ids:
        return
    if type(job_ids) is not list:
        job_ids = [job_ids]

    if timeout == 0:
        timeout = sys.maxint

    start = time.time()

    while True:
        busy_job_ids = job_ids[10:]

        # at most 10 jobs a time.
        job_set = API.conn.call('DescribeJobs', {
            'jobIds': job_ids[0:10]
        })['jobSet']

        # maybe the job is not store in db yet. try later.
        if len(job_set) == 0:
            sleep(2)
            continue

        busy_jobs = []
        for job in job_set:
            # if one is busy, go check next job.
            if job['status'] in('pending', 'running'):
                busy_jobs.append(job)
                busy_job_ids.append(job['jobId'])
                continue

            # if one job is failed, raise exception
            if job['status'] == 'error':
                raise Exception(
                    "Job (%s) failed, action: %s, resourceIds: %s" %
                    (job['jobId'], job['action'], job['resourceIds']))

        if not busy_job_ids:
            break

        sleep(4)

        job_ids = busy_job_ids

        if time.time() - start > timeout:
            job_status = dict((j['jobId'], j['status']) for j in busy_jobs)
            raise Exception('wait_for_job timeout. '
                            'job => status map: %s' % job_status)
