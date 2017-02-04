# -*- coding: utf-8 -*-

from analyzer.model import Article


class Rating(object):

    MAX_GAIN = 10.0
    DISCOUNT = 0.5
    '''
    Rating calculate rating of each authors given articles
    according topic model.
    '''

    def __init__(self, articles):
        self.articles = articles
        # Rating result is calculated like key-value between author and rate
        # e.g. {author1: 98, author2: 12, author3: 43, ... }
        ratings = self.calc()

    def unique_authors(self):
        return set([a.author for a in self.articles])

    def unique_topics(self):
        '''
        List of unique topics given articles
        :param articles:
        :return: list of unique topic ids
        '''
        x = []
        for a in self.articles:
            x.extend(a.topics)
        unique_topics = set([t[0] for t in x])
        return unique_topics

    def num_unique_topics(self):
        '''
        Number of unique topics
        :param articles:
        :return: number of unique topics
        '''
        return len(self.unique_topics())

    def calc(self):
        '''
        Calculate rating of each authors
        :return: key-value dictionary of author and their rating
        '''
        ret = {a.id: 0 for a in self.unique_authors()}
        unique_topics = self.unique_topics()
        # Select above 50% articles sorted by topic probability
        max_num = max(int(len(self.articles) * 0.5), 3)
        for t in unique_topics:
            sorted_by_topic = list(reversed(sorted([a for a in self.articles],
                                                   key=lambda a: a.get_topic_prob(t))))
            sorted_by_time = list(sorted(sorted_by_topic[:max_num],
                                         key=lambda a: a.pub_time))

            gain = Rating.MAX_GAIN
            for s in sorted_by_time:
                ret[s.author.id] += gain
                gain *= Rating.DISCOUNT

        self.rating = ret
        return self.rating

    def get_author_rate(self, author_id):
        return self.rating[author_id]
