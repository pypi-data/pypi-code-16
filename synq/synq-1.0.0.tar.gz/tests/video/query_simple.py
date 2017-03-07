import unittest
import os

try:
    synq_api_key = os.environ['SYNQ_API_KEY']
except KeyError as e:
    print("** ERROR: Environment variable $SYNQ_API_KEY must be set to run tests!")
    exit(1)

class TestQueryExactMethod(unittest.TestCase):

    def test_query_simple(self):
        import synq
        va = synq.VideoAPI(synq_api_key)
        # Retrieve all videos that have file-state "uploaded"
        res = va.query_simple("state", "uploaded")
        # STOP EXAMPLE FOR videos__query_simple
        assert(isinstance(res, list))

    def test_query_simple_for_nonexistant(self):
        import synq
        va = synq.VideoAPI(synq_api_key)
        res = va.query_simple("bogus", "value")
        # shouldn't match anything!
        assert(res == [])

    def test_query_simple_for_userdata(self):
        import synq, uuid
        va = synq.VideoAPI(synq_api_key)
        my_uuid = uuid.uuid4().hex
        video_id = va.create(userdata={"uuid":my_uuid})['video_id']
        res = va.query_simple( "userdata.uuid", my_uuid)
        assert(len(res) == 1)
        assert(res[0]['userdata']['uuid'] == my_uuid)

    def test_query_simple_for_metadata(self):
        import synq, uuid
        va = synq.VideoAPI(synq_api_key)
        video_id = va.create()['video_id']
        res = va.query_simple("video_id", video_id)
        assert(len(res) == 1)
        assert(res[0]['video_id'] == video_id)

if __name__ == '__main__':
    unittest.main()
