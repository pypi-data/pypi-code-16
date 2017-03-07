import unittest
import os

try:
    synq_api_key = os.environ['SYNQ_API_KEY']
except KeyError as e:
    print("** ERROR: Environment variable $SYNQ_API_KEY must be set to run tests!")
    exit(1)

class TestQueryMethod(unittest.TestCase):

    def test_query(self):
        # START EXAMPLE FOR videos__query_exact
        import synq
        va = synq.VideoAPI(synq_api_key)
        # Retrieve all videos
        res = va.query("return video")
        # Retrieve the _title field and number of views from all videos that have file-state "uploaded"
        res = va.query("""
if(video.file_state == "uploaded")
return video.pick("player")
""")
        # STOP EXAMPLE FOR videos__query_exact
        assert(type(res) == type([]))


if __name__ == '__main__':
    unittest.main()
