from plato_clean.cases import wait_for_job
from plato_clean.cases import get_resource
from plato_clean.cases import wait_busy_resource
from plato_clean.cases import post_resource

class CleanVolumes():

    def run(self, API, sleep):
        wait_busy_resource(API, 'DescribeVolumes', {
            'status': ['pending', 'attaching', 'detaching',
                       'backup_ing', 'backup_restoring'],
        }, sleep)

        volumes = get_resource(API, 'DescribeVolumes', {
            'status': ['active', 'inuse', 'error']
        }, 'volumeSet')

        # detach volumes
        job_ids = []
        for volume in volumes:
            if volume['instanceId']:
                result = API.conn.call('DetachVolumes', {
                    'volumeIds': [volume['volumeId']],
                    'instanceId': volume['instanceId']
                })

                job_ids.append(result['jobId'])

        wait_for_job(API, job_ids, sleep)

        volume_ids = [v['volumeId'] for v in volumes]
        post_resource(API, 'DeleteVolumes', volume_ids, 'volumeIds')
