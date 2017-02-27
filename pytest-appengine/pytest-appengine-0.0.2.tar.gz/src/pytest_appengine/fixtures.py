# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import pytest

ROOT_DIR = ''


class AppEngineWebapp(object):
    def __init__(self):
        self.testbed = None

    def setup(self):
        from google.appengine.ext import testbed
        self.testbed = testbed.Testbed()

        self.testbed.activate()
        self.testbed.setup_env(overwrite=True, APPLICATION_ID='_')

        # INIT ALL THE STUBS!
        self.testbed.init_app_identity_stub()
        self.testbed.init_blobstore_stub()
        self.testbed.init_capability_stub()
        self.testbed.init_channel_stub()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_files_stub()
        # uncomment the below line to enable testing against the images API
        # self.testbed.init_images_stub()
        self.testbed.init_logservice_stub()
        self.testbed.init_mail_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_taskqueue_stub(root_path=ROOT_DIR)
        self.testbed.init_urlfetch_stub()
        self.testbed.init_user_stub()
        self.testbed.init_xmpp_stub()

        #self.taskq_stub = test_bed.get_stub(testbed.TASKQUEUE_SERVICE_NAME)
        #self.mail_stub = test_bed.get_stub(testbed.MAIL_SERVICE_NAME)

    def teardown(self):
        self.testbed.deactivate()

    def login(self, email='user@example.com', id='123', is_admin=False):
        self.testbed.setup_env(
            user_email=email,
            user_id=id,
            user_is_admin='1' if is_admin else '0',
            overwrite=True
        )


@pytest.fixture(scope='module')
def appengine():
    """ AppEngine test bed. """
    tbed = AppEngineWebapp()
    tbed.setup()

    yield tbed

    tbed.teardown()
