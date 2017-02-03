import argparse
import git
import mock
import os
import shutil
import tempfile
import unittest
import subprocess

from kubos.test import utils
from kubos import update

class KubosTestUpdate(utils.KubosTestCase):

    def setUp(self):
        super(KubosTestUpdate, self).setUp()
        #unfortunately overriding the os.path.expanduser function to point to
        #self.base_dir causes all kinds of side effects and errors
        update.KUBOS_DIR = os.path.join(self.base_dir, '.kubos')
        update.KUBOS_SRC_DIR = os.path.join(update.KUBOS_DIR, 'kubos')
        update.KUBOS_EXAMPLE_DIR = os.path.join(update.KUBOS_DIR, 'example')
        update.KUBOS_GIT_DIR = os.path.join(update.KUBOS_SRC_DIR, '.git')


    def test_update(self):
        '''
        Testing the inital kubos source tree cloning
        '''
        args = argparse.Namespace()
        args.set_version = None
        update.execCommand(args, None)
        self.assertTrue(os.path.isdir(update.KUBOS_GIT_DIR))


    def test_update_already_existing(self):
        '''
        Testing the update (pulling of tags) on a pre-existing kubos source tree
        '''
        #Set up the kubos src tree
        update.fetch_tags = mock.MagicMock()
        os.makedirs(update.KUBOS_DIR)
        os.chdir(update.KUBOS_DIR)
        DEV_NULL = open(os.devnull, 'w')
        subprocess.call(['git', 'clone', '-n', update.KUBOS_SRC_URL], stdout=DEV_NULL)

        #Done setting up the initial kubos source tree
        update.fetch_tags = mock.MagicMock()
        args = argparse.Namespace()
        args.set_version = None
        self.assertTrue(os.path.isdir(update.KUBOS_GIT_DIR))
        update.execCommand(args, None)
        self.assertTrue(update.fetch_tags.called)


    def tearDown(self):
        super(KubosTestUpdate, self).tearDown()


if __name__ == '__main__':
    unittest.main()
