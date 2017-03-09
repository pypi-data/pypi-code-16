from plato_clean.cases import get_resource
from plato_clean.cases import post_resource


class CleanEips():

    def run(self, API, sleep):
        eips = get_resource(API, 'DescribeEips', {
            'status': ['active', 'associated'],
        }, 'eipSet')

        # dissociate eips
        eip_ids = [e['eipId'] for e in eips if e['resourceId']]
        post_resource(API, 'DissociateEips', eip_ids, 'eipIds')

        eip_ids = [e['eipId'] for e in eips]
        post_resource(API, 'ReleaseEips', eip_ids, 'eipIds')
