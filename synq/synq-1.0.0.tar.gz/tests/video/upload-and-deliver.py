import unittest
import os

try:
    synq_api_key = os.environ['SYNQ_API_KEY']
except KeyError as e:
    print(
        "** ERROR: Environment variable $SYNQ_API_KEY must be set to run tests!")
    exit(1)


class TestUploadAndDeliverMethod(unittest.TestCase):

    def test_upload_and_deliver(self):
        import os.path
        if not os.path.isfile("test.mp4"):
            raise unittest.SkipTest(
                "File 'test.mp4' not found, skipping upload test. Add a valid video-file to the test-folder to execute this test.")

        import synq
        va = synq.VideoAPI(synq_api_key)

        video_id = va.create(synq_api_key)['video_id']

        res = va.upload( video_id).to_dict()

        import requests
        fh = open('test.mp4', 'rb')
        r = requests.post(res['action'], files={'file': fh}, data={
            "AWSAccessKeyId": res['aws_access_key_id'],
            "Content-Type": res['content_type'],
            "Policy": res['policy'],
            "Signature": res['signature'],
            "acl": res['acl'],
            "key": res['key']
        })
        fh.close()
        self.assertEqual(204, r.status_code, msg=r.text)


if __name__ == '__main__':
    unittest.main()
