from cubicweb.devtools.testlib import AutomaticWebTest


class AutomaticWebTest(AutomaticWebTest):

    def to_test_etypes(self):
        return set()

    def list_startup_views(self):
        return ('registration',)


if __name__ == '__main__':
    import unittest
    unittest.main()
