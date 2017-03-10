from plato_clean.cases import get_resource
from plato_clean.cases import wait_busy_resource
from plato_clean.cases import post_resource


class CleanImages():

    def run(self, API, sleep):
        wait_busy_resource(API, 'DescribeImages', {
            'status': ['pending'],
            'isPublic': False
        }, sleep)

        images = get_resource(API, 'DescribeImages', {
            'status': ['active', 'error'],
            'isPublic': False
        }, 'imageSet')

        image_ids = [i['imageId'] for i in images]
        post_resource(API, 'DeleteImages', image_ids, 'imageIds')
