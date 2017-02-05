import os
import pytest
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
        article = Article(1, a, datetime.combine(d, t), "http://example.com", topics)
        assert article.author == a
        assert article.pub_time.year == 2017
        assert len(article.topics) == 3

    @pytest.mark.skip(reason="depends on remote MySQL")
    def test_author_db(self):
        user = os.environ.get('PTI_USER')
        password = os.environ.get('PTI_PASSWORD')
        host = os.environ.get('PTI_HOST')
        db = os.environ.get('PTI_DB')
        authors = Author.load_from_mysql(user, password, host, db)
        assert len(authors) == 1

    @pytest.mark.skip(reason="no pickle file in predefined dir")
    def test_article_db(self):
        user = os.environ.get('PTI_USER')
        password = os.environ.get('PTI_PASSWORD')
        host = os.environ.get('PTI_HOST')
        db = os.environ.get('PTI_DB')
        articles = Article.load_from_mysql(user, password, host, db)
        assert len(articles) == 2

    def test_pickle_load(self):
        t = Article.load_from_pickel("./data", 1)
        assert len(t) == 2

