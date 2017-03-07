import unittest
import os

try:
    synq_api_key = os.environ['SYNQ_API_KEY']
except KeyError as e:
    print("** ERROR: Environment variable $SYNQ_API_KEY must be set to run tests!")
    exit(1)

class TestCreateMethod(unittest.TestCase):

    def test_create(self):
        # START EXAMPLE FOR videos__create
        import synq
        va = synq.VideoAPI(synq_api_key)
        # Create a new video
        res = va.create()
        # The returned object contains embed URL, thumbnail URL,
        # video ID and all other metadata associated with the video.

        # Create a new video with some metadata
        res = va.create(userdata={"next_in_playlist":"78d1ca98042648b7808ddff027a1c23e"})
        # STOP EXAMPLE FOR videos__create
        assert(res['userdata']['next_in_playlist'] == "78d1ca98042648b7808ddff027a1c23e")

    def test_create_userdata_empty_by_default(self):
        import synq
        va = synq.VideoAPI(synq_api_key)
        userdata = va.create()['userdata']
        assert(userdata == {})

if __name__ == '__main__':
    unittest.main()
