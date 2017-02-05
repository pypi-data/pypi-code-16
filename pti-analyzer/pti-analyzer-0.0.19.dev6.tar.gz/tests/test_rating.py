from datetime import datetime, date, time

from analyzer.model import Article
from analyzer.model import Author
from analyzer.rating import Rating


class TestRating(object):
    articles = [
        Article(0, Author(0, "Kai",       0), datetime(2017, 1, 23), "http://a.com", [(0, 0.1), (1, 0.2), (2, 0.3)]),
        Article(1, Author(1, "Publisher", 0), datetime(2017, 1, 24), "http://b.com", [(0, 0.3), (1, 0.2), (2, 0.1)]),
        Article(2, Author(2, "Gologo",    0), datetime(2017, 1, 25), "http://c.com", [(0, 0.6), (1, 0.3), (2, 0.9)]),
        Article(3, Author(3, "Yamada",    0), datetime(2017, 1, 26), "http://d.com", [(0, 0.6), (1, 0.3), (2, 0.9)]),
        Article(4, Author(2, "Gologo",    0), datetime(2017, 1, 27), "http://e.com", [(0, 0.1), (1, 0.5), (2, 0.1)]),
        Article(5, Author(2, "Gologo",    0), datetime(2017, 1, 28), "http://f.com", [(0, 0.6), (1, 0.2), (2, 0.4)])
    ]

    rating = Rating(articles)

    def test_extract_topics(self):
        topics = TestRating.rating.unique_topics()
        assert len(topics) == 3

    def test_num_unique_topics(self):
        num_topics = TestRating.rating.num_unique_topics()
        assert num_topics == 3

    def test_unique_author(self):
        unique_authors = TestRating.rating.unique_authors()
        assert len(unique_authors) == 4

    def test_rating_calculation(self):
        ret = TestRating.rating.calc()
        assert len(ret) == 4
        assert ret[0] == 0
        assert ret[1] == 0
        assert ret[2] == 0
        assert ret[3] == -0.23105857863000487
