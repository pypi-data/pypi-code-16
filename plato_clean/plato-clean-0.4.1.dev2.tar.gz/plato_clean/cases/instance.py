from plato_clean.cases import get_resource
from plato_clean.cases import wait_busy_resource
from plato_clean.cases import post_resource


class CleanInstances():

    def run(self, API, sleep):
        wait_busy_resource(API, 'DescribeInstances', {
            'status': ['pending', 'starting', 'stopping',
                       'restarting', 'scheduling']
        }, sleep)

        instances = get_resource(API, 'DescribeInstances', {
            'status': ['active', 'stopped', 'error']
        }, 'instanceSet')

        # delete instances
        instance_ids = [i['instanceId'] for i in instances]
        post_resource(API, 'DeleteInstances', instance_ids, 'instanceIds')
