# -*- coding: utf-8 -*-

import pymysql.cursors
import pickle


class Author(object):
    '''
    Author represents a author of article which keeps
    rating of the author.
    '''

    @classmethod
    def load_from_mysql(cls, user, password, host, database):
        conn = pymysql.connect(user=user, password=password,
                               host=host, database=database)

        try:
            with conn.cursor() as cur:
                sql = "SELECT id,name,rate from articles_authors;"
                cur.execute(sql)
                ret = [Author(r[0], r[1], r[2]) for r in cur.fetchall()]
        finally:
            conn.close()

        return ret

    def save(self, user, password, host, database):
        conn = pymysql.connect(user=user, password=password,
                               host=host, database=database)

        try:
            with conn.cursor() as cur:
                sql = "UPDATE articles_authors " \
                      "  SET rate=%s " \
                      "  WHERE id=%s;"
                cur.execute(sql, (str(self.rate), self.id))
        finally:
            conn.close()

        return

    def __init__(self, id, name, rate):
        self.id = id
        self.name = name
        self.rate = rate

    def __eq__(self, other):
        assert type(other) is Author
        return self.name == other.name and self.id == other.id

    def __ne__(self, other):
        assert type(other) is Author
        return self.name != other.name and self.id == other.id

    def __hash__(self):
        return self.id.__hash__()


class Article(object):
    '''
    Article represents a article by a author.
    '''

    @classmethod
    def load_from_mysql(cls, user, password, host, database, pkl_base_dir):
        conn = pymysql.connect(user=user, password=password,
                               host=host, database=database)

        ret = []
        try:
            with conn.cursor() as cur:
                sql = "select " \
                      "  art.id," \
                      "  art.pub_date," \
                      "  art.url," \
                      "  auh.id," \
                      "  auh.name," \
                      "  auh.rate " \
                      "from " \
                      "  articles_articles art " \
                      "JOIN " \
                      "  articles_authors auh " \
                      "on art.author_id = auh.id;"
                cur.execute(sql)

                for r in cur.fetchall():
                    try:
                        topics = Article.load_from_pickel(pkl_base_dir, r[0])
                        a = Article(r[0], Author(r[3], r[4], r[5]), r[1], r[2], topics)
                        ret.append(a)
                    except FileNotFoundError as e:
                        print("File Not Found", e)

        finally:
            conn.close()

        return ret

    @classmethod
    def load_from_pickel(cls, base_dir, id):
        return pickle.load(open("{}/{}.pkl".format(base_dir, id), "rb"))

    def __init__(self, id, author, pub_time, url, topics):

        self.id = id
        self.author = author
        self.pub_time = pub_time
        self.url = url
        # Topics is a list of tuple of topic category and probability.
        # e.g. [(1, 0.12), (2, 0.14), (3, 0.98),...]
        self.topics = topics

    def get_topic_prob(self, t_id):

        '''
        Get probability of given topic id
        :param t_id:
        :return: probability
        '''
        for t in self.topics:
            if t[0] == t_id:
                return t[1]

        return None
