import unittest
from socialbakers.api import SocialbakersApi
from socialbakers.objects.socialnetworkobject import (
	SocialNetworkObject,
	FacebookObject,
	TwitterObject,
	BlaObject
	)

from unittest import TestCase


class SocialnetworkObject(unittest.TestCase):
	global token, secret
	token = 'MjMzNzcyXzM5MzM0NV8xNzkyNDA4OTE5MjQ3XzUzYzUwNjU2YzQyN2MyOGUyOTY2MTdiNGU1YTc0Zjhh'
	secret = '5aa58b075ebb8e92d5d8b72da1b1ccac'
	SocialbakersApi.init(token,secret)

	def test_socialnetworkobject_time_range(self):
		fb = FacebookObject()
		self.assertEqual(1,fb.get_bulk_metrics('2017-01-01','2017-01-02'))

if __name__ == '__main__':
	unittest.main()
