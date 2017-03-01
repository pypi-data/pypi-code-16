import unittest
import shaman.src.helpers.train_sets as train_sets
from shaman.src.helpers.tree_searcher import Searcher


class TestSearcher(unittest.TestCase):
    def test_simple_one_search(self):
        url = 'google.com'
        res = 1

        searcher = Searcher()

        searcher.train(url,res)

        search_res = searcher.search(url)
        self.assertSetEqual(search_res,set([1,]))

    def test_simple_two_search(self):
        url = 'http://google.com'
        res = 1

        searcher = Searcher()

        searcher.train(url,res)

        search_res = searcher.search(url)
        self.assertSetEqual(search_res,set([1,]))


    def test_simple_multiple_search(self):
        urls = [('google.com',1),('google.com/search',2)]

        searcher = Searcher()

        for url in urls:
            searcher.train(url[0],url[1])

        search_res = searcher.search('google.com/search')
        self.assertSetEqual(search_res,set([1,2]))

    def test_real_rutracker(self):
        result_must_be = set([3619,])

        searcher = Searcher()

        for rule in train_sets.train_rutracker_set:
            url = rule[1]
            seg = rule[0]

            if url.startswith('http'):
                url = url[4:]
                if url.startswith('s'):
                    url = url[4:]
                else:
                    url = url[3:]

            searcher.train(url, seg)

        rutracker_search_result = searcher.search('rutracker.org')
        self.assertSetEqual(result_must_be, rutracker_search_result)


    def test_real_rutracker_2(self):
        result_must_be = set([2788, 3619, 3782, 3783])

        searcher = Searcher()

        for rule in train_sets.train_rutracker_set:
            url = rule[1]
            seg = rule[0]

            if url.startswith('http'):
                url = url[4:]
                if url.startswith('s'):
                    url = url[4:]
                else:
                    url = url[3:]

            searcher.train(url, seg)

        rutracker_search_result = searcher.search('rutracker.org/forum/viewtopic.php?t=1008823')
        self.assertSetEqual(result_must_be, rutracker_search_result)


    def test_real_rutracker_forum(self):
        searcher = Searcher()

        for rule in train_sets.train_rutracker_forum:
            url = rule[1]
            seg = rule[0]

            if url.startswith('http'):
                url = url[4:]
                if url.startswith('s'):
                    url = url[4:]
                else:
                    url = url[3:]

            searcher.train(url, seg)

        rutracker_search_result = searcher.search('rutracker.org/forum/viewtopic.php?t=3470031')
        self.assertTrue(2788 in rutracker_search_result)

    def test_real_ee24(self):
        result_must_be = set([185, 2200, 2762, 3067, 3294])

        searcher = Searcher()

        for rule in train_sets.train_ee24_set:
            url = rule[1]
            seg = rule[0]

            if url.startswith('http'):
                url = url[4:]
                if url.startswith('s'):
                    url = url[4:]
                else:
                    url = url[3:]

            searcher.train(url, seg)

        rutracker_search_result = searcher.search('ee24.ru/france/apartments/provans-alpy-lazurnyj-bereg/antib/267885')
        self.assertSetEqual(result_must_be, rutracker_search_result)

    def test_real_adento(self):
        result_must_be = set([2465, 3058, 3911])

        searcher = Searcher()

        for rule in train_sets.train_adento_set:
            url = rule[1]
            seg = rule[0]

            if url.startswith('http'):
                url = url[4:]
                if url.startswith('s'):
                    url = url[4:]
                else:
                    url = url[3:]

            searcher.train(url, seg)

        rutracker_search_result = searcher.search('adento.ru/polost_rta.html')
        self.assertSetEqual(result_must_be, rutracker_search_result)

if __name__ == '__main__':
    unittest.main()