import unittest
import os

try:
    synq_api_key = os.environ['SYNQ_API_KEY']
except KeyError as e:
    print("** ERROR: Environment variable $SYNQ_API_KEY must be set to run tests!")
    exit(1)

class TestUploadMethod(unittest.TestCase):

    def test_upload(self):
        # START EXAMPLE FOR videos__upload
        import synq
        va = synq.VideoAPI(synq_api_key)
        # Create a new video
        video_id = va.create()['video_id']
        # The returned object contains embed URL, thumbnail URL,
        # video ID and all other metadata associated with the video.

        # upload the video
        res = va.upload(video_id)
        # STOP EXAMPLE FOR videos__upload

        # TODO: probably figure out something better to test for here.
        assert(res['acl'] == 'public-read')

    def test_upload_without_create(self):
        # START EXAMPLE FOR videos__upload
        import synq
        va = synq.VideoAPI(synq_api_key)
        
        # upload the video
        res = va.upload()
        # STOP EXAMPLE FOR videos__upload

        # TODO: probably figure out something better to test for here.
        assert(res['acl'] == 'public-read')
if __name__ == '__main__':
    unittest.main()
