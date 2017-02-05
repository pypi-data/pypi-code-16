import os

from analyzer.rating import Rating
from analyzer.model import Author
from analyzer.model import Article

def rating():
    user = os.environ.get('PTI_USER')
    password = os.environ.get('PTI_PASSWORD')
    host = os.environ.get('PTI_HOST')
    db = os.environ.get('PTI_DB')
    articles = Article.load_from_mysql(user, password, host, db, '/var/pti/topic')
    r = Rating(articles)
    r.calc()
    authors = Author.load_from_mysql(user, password, host, db)
    for a in authors:
        rate = r.get_author_rate(a.id)
        a.rate = rate
        a.save(user, password, host, db)

if __name__ == "__main__":
    rating()