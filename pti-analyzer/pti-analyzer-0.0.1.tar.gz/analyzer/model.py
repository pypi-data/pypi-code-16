# -*- coding: utf-8 -*-

class Author(object):
    '''
    Author represents a author of article which keeps
    rating of the author.
    '''

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

    def __init__(self, author, published_time, url, topics):
        self.author = author
        self.published_time = published_time
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
