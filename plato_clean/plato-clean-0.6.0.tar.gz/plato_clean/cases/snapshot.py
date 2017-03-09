# from plato_clean.cases import wait_for_job
# from plato_clean.cases import get_resource
# from plato_clean.cases import post_resource


class CleanSnapshots():

    def run(self, API, sleep):
        pass
#         snapshots = get_resource(API, 'DescribeSnapshots',{
#             'status': ['active', 'error'],
#         }, 'snapshotSet')

#         snapshot_ids = [i['snapshotId'] for i in snapshots]

#         post_resource(API, 'DeleteSnapshots', snapshot_ids, 'snapshotIds')
