import unittest

from owbd_file_and_data_utilities import list_tools


class TestFilterList(unittest.TestCase):

    def setUp(self):
        self.input_list = [u'.testfile.txt', u'something', u'a_file.json', u'1.txt', u'filter_me_1',
                           u'2.txt', u'filter_me_2', u'3.txt', u'filter_me_3', u'something_else']

        self.filters = [u'filter_me', u'some']

    def tearDown(self):
        pass

    def test_no_filter_exclude_false(self):

        output = list_tools.filter_list(filter_list=list(self.input_list),
                                        filters=[],
                                        exclude=False)

        expected_output = []

        self.assertEqual(expected_output,
                         output,
                         msg=u'No Filter, exclude=False; Not working as expected')

    def test_no_filter_exclude_true(self):

        output = list_tools.filter_list(filter_list=list(self.input_list),
                                        filters=[],
                                        exclude=True)

        expected_output = [u'something', u'a_file.json', u'1.txt', u'filter_me_1',
                           u'2.txt', u'filter_me_2', u'3.txt', u'filter_me_3', u'something_else']

        self.assertEqual(expected_output,
                         output,
                         msg=u'No Filter, exclude=True; Not working as expected')

    def test_exclude_false(self):

        output = list_tools.filter_list(filter_list=list(self.input_list),
                                        filters=self.filters,
                                        exclude=False)

        expected_output = [u'something', u'filter_me_1', u'filter_me_2', u'filter_me_3', u'something_else']

        self.assertEqual(expected_output,
                         output,
                         msg=u'exclude=False; Not working as expected')

    def test_exclude_true(self):

        output = list_tools.filter_list(filter_list=list(self.input_list),
                                        filters=self.filters,
                                        exclude=True)

        expected_output = [u'a_file.json', u'1.txt', u'2.txt', u'3.txt']

        self.assertEqual(expected_output,
                         output,
                         msg=u'exclude=True; Not working as expected')


if __name__ == u'__main__':
    unittest.main()
