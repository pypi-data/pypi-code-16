import unittest
import json
import httpretty
from pivotalpy.client import PivotalClient

PROJECT_ID = '5'
STORY_ID = '2'
TOKEN = 'Token'
BASE_STORIES_URL = 'https://www.pivotaltracker.com/services/v5/projects/' + PROJECT_ID + '/stories/'

class TestStories(unittest.TestCase):
    def setUp(self):
        self.driver = PivotalClient(TOKEN)

    def test_init(self):
        self.assertEquals(self.driver.auth.token, 'Token')

    # Test that exceptions are thrown when we get a bad response from Pivotal
    @httpretty.activate
    def test_api_fail(self):
        httpretty.register_uri(httpretty.GET, BASE_STORIES_URL, body='Fail', status=400)
        httpretty.register_uri(httpretty.POST, BASE_STORIES_URL, body='Fail', status=400)
        httpretty.register_uri(httpretty.GET, BASE_STORIES_URL + STORY_ID + '/', body='Fail', status=400)
        httpretty.register_uri(httpretty.PUT, BASE_STORIES_URL + STORY_ID + '/', body='Fail', status=400)

        with self.assertRaises(IOError):
            r = self.driver.story.get_all(PROJECT_ID)
            self.assertEquals(r.status_code, 400)

        with self.assertRaises(IOError):
            r = self.driver.story.get(PROJECT_ID, STORY_ID)
            self.assertEquals(r.status_code, 400)

        with self.assertRaises(IOError):
            r = self.driver.story.create(PROJECT_ID, None)
            self.assertEquals(r.status_code, 400)

        with self.assertRaises(IOError):
            r = self.driver.story.update(PROJECT_ID, STORY_ID, None)
            self.assertEquals(r.status_code, 400)

        with self.assertRaises(IOError):
            r = self.driver.story.post_comment(PROJECT_ID, STORY_ID, None)
            self.assertEquals(r.status_code, 400)

    @httpretty.activate
    def test_get_all(self):
        body = json.dumps([
            {'story_id' : '2'},
            {'story_id' : '3'},
            {'story_id' : '4'}
        ])

        httpretty.register_uri(httpretty.GET, BASE_STORIES_URL, body=body, status=200)

	r = self.driver.story.get_all(PROJECT_ID)

        self.assertEquals(r[0]['story_id'], '2')
        self.assertEquals(r[1]['story_id'], '3')
        self.assertEquals(r[2]['story_id'], '4')

    @httpretty.activate
    def test_create_story(self):
        body = json.dumps({ 'name' : 'A Story', 'story_type' : 'feature', 'kind' : 'story'})

        httpretty.register_uri(httpretty.POST, BASE_STORIES_URL, body=body, status=200)

        r = self.driver.story.create(PROJECT_ID, body)

        self.assertEquals(r['name'], 'A Story')
        self.assertEquals(r['story_type'], 'feature')
        self.assertEquals(r['kind'], 'story')

    @httpretty.activate
    def test_get_story(self):
        body = json.dumps({ 'name' : 'A Story', 'story_type' : 'feature', 'kind' : 'story'})

        httpretty.register_uri(httpretty.GET, BASE_STORIES_URL + STORY_ID + '/', body=body, status=200)

        r = self.driver.story.get(PROJECT_ID, STORY_ID)

        self.assertEquals(r['name'], 'A Story')
        self.assertEquals(r['story_type'], 'feature')
        self.assertEquals(r['kind'], 'story')

    @httpretty.activate
    def test_update_story(self):
        body = json.dumps({ 'story_type' : 'bug'})

        httpretty.register_uri(httpretty.PUT, BASE_STORIES_URL + STORY_ID + '/', body=body, status=200)

        r = self.driver.story.update(PROJECT_ID, STORY_ID)

        self.assertEquals(r['story_type'], 'bug')

    @httpretty.activate
    def test_update_story(self):
        body = json.dumps({ 'kind' : 'comment'})

        httpretty.register_uri(httpretty.POST, BASE_STORIES_URL + STORY_ID + '/comments/', body=body, status=200)

        r = self.driver.story.post_comment(PROJECT_ID, STORY_ID, { 'text' : 'A comment' })

        self.assertEquals(r['kind'], 'comment')
