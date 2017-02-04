from datetime import datetime, date, time

from analyzer.model import Article
from analyzer.model import Author


class TestModel:
    def test_author_name(self):
        a = Author(0, "Kai", 3)
        assert a.name == "Kai"

    def test_article_name(self):
        a = Author(0, "Kai", 3)
        d = date(2017, 2, 4)
        t = time(13, 22)
        topics = [(1, 0.32), (2, 0.12), (3, 0.21)]
        article = Article(a, datetime.combine(d, t), "http://example.com", topics)
        assert article.author == a
        assert article.published_time.year == 2017
        assert len(article.topics) == 3