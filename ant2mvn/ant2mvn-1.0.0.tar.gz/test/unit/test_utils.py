# -*- coding: utf-8 -*-

import unittest

from ant2mvn import utils


class TestUtils(unittest.TestCase):

    def test_mvn_sha1_search(self):
        f = utils.get_files('../resources/lib/', '.jar')[0]

        self.assertEqual(f, '../resources/lib/activation-1.1.jar')

        with open(f, 'rb') as file:
            s = utils.sha1(file.read())

            api = utils.MavenCentralRepoRestSearchApi('maven_central_repo', 'search.maven.org')
            r = api.sha1_search(s)

        self.assertEqual(r['response']['docs'][0]['id'], 'javax.activation:activation:1.1')


if __name__ == '__main__':
    unittest.main()
