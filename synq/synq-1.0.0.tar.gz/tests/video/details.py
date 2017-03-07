import unittest
import os

try:
    synq_api_key = os.environ['SYNQ_API_KEY']
except KeyError as e:
    print("** ERROR: Environment variable $SYNQ_API_KEY must be set to run tests!")
    exit(1)

class TestDetailsMethod(unittest.TestCase):

    def test_details(self):
        # START EXAMPLE FOR video__details
        import synq
        va = synq.VideoAPI(synq_api_key)
        # First create a video we can query
        video_id = va.create()['video_id']
        # Retrieve details about the video
        res = va.details(video_id)
        # STOP EXAMPLE FOR videos__details
        assert(isinstance(res, dict))

    def test_details_with_userdata(self):

        import synq
        va = synq.VideoAPI(synq_api_key)
        video_id = va.create(userdata={"next_in_playlist":"78d1ca98042648b7808ddff027a1c23e"})['video_id']
        res = va.details(video_id)
        assert(res['userdata']['next_in_playlist'] == "78d1ca98042648b7808ddff027a1c23e")

if __name__ == '__main__':
    unittest.main()
