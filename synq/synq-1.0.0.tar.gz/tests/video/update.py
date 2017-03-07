import unittest
import os

try:
    synq_api_key = os.environ['SYNQ_API_KEY']
except KeyError as e:
    print("** ERROR: Environment variable $SYNQ_API_KEY must be set to run tests!")
    exit(1)

class TestUpdateMethod(unittest.TestCase):

    def test_update(self):
        # START EXAMPLE FOR videos__update
        import synq, json
        va = synq.VideoAPI(synq_api_key)
        # Create a new video
        video_id = va.create()['video_id']
        # Associate a new piece of metadata with the video
        va.update(video_id, "video.userdata = {0}".format(json.dumps({"next_in_playlist":"78d1ca98042648b7808ddff027a1c23f"})))
        # STOP EXAMPLE FOR videos__update
        res = va.details(video_id)
        assert(res['userdata']['next_in_playlist'] == "78d1ca98042648b7808ddff027a1c23f")

    def test_update_set_bogus_user_object(self):
        # test that error occurs on wrong userdata
        import synq, json
        va = synq.VideoAPI(synq_api_key)
        # Create a new video
        video_id = va.create()['video_id']
        # Associate a new piece of metadata with the video
        try:
            va.update( video_id, "video.userdata = {0}".format(json.dumps("78d1ca98042648b7808ddff027a1c23f")))        
        except Exception as e:
            return
        assert(False);

if __name__ == '__main__':
    unittest.main()
