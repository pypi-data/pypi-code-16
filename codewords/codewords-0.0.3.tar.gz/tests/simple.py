import unittest
from mock import mock_open, patch
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
from codewords import CodeWordGenerator


class CodeWordsTests(unittest.TestCase):
    def setUp(self):
        adjfile = StringIO("loud")
        nounfile = StringIO("thunderstorm")
        delfile = StringIO("-")
        self.cw = CodeWordGenerator(adjfile=adjfile, nounfile=nounfile,
                                    delimiterfile=delfile)

    def test_simple_code_word_generation(self):
        self.assertEqual(self.cw.generate(), "loud-thunderstorm")


class CodeWordsFileTest(unittest.TestCase):
    def setUp(self):
        self.adjfile = StringIO("loud")
        self.nounfile = StringIO("thunderstorm")
        self.delfile = StringIO("-")

    def test_read_from_adjective_file(self):
        with patch('codewords.gen.open', mock_open(read_data='loud')) as m:
            cwg = CodeWordGenerator(adjfilename="adjfile.txt", nounfilename=None,
                                    delimiterfilename=None, nounfile=self.nounfile,
                                    delimiterfile=self.delfile)
        m.assert_called_once_with("adjfile.txt", "r")
        self.assertEqual(cwg.generate(), "loud-thunderstorm")
        assert cwg.adjective_list == ['loud']

    def test_read_from_noun_file(self):
        with patch('codewords.gen.open', mock_open(read_data='thunderstorm')) as m:
            cwg = CodeWordGenerator(adjfilename=None, nounfilename="nounfile.txt",
                                    delimiterfilename=None, adjfile=self.adjfile,
                                    delimiterfile=self.delfile)
        m.assert_called_once_with("nounfile.txt", "r")
        self.assertEqual(cwg.generate(), "loud-thunderstorm")
        assert cwg.noun_list == ['thunderstorm']

    def test_read_from_delimiter_file(self):
        with patch('codewords.gen.open', mock_open(read_data='-')) as m:
            cwg = CodeWordGenerator(adjfilename=None, nounfilename=None,
                                    delimiterfilename="delfile.txt", adjfile=self.adjfile,
                                    nounfile=self.nounfile)
        m.assert_called_once_with("delfile.txt", "r")
        self.assertEqual(cwg.generate(), "loud-thunderstorm")
        assert cwg.delimiter_list == ['-']
