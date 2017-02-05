# -*- coding: utf-8 -*-

import numpy as np
from analyzer.model import Article


class Rating(object):

    MAX_GAIN = 10.0
    DISCOUNT = 0.5
    RATING_BASE = 1.0
    MAX_ARTICLES = 5
    TOPIC_PROB_THRESHOLD = 0.5
    PUBLISHER_ID = 11
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
        author_articles = {a.id: 0 for a in self.unique_authors()}
        unique_topics = self.unique_topics()

        for t in unique_topics:
            # Filter topic related articles
            related_articles = [art for art in self.articles
                                 if art.get_topic_prob(t) >= Rating.TOPIC_PROB_THRESHOLD]

            # Sorted by time in descending order
            # First articles should get lower points because it's published late.
            sorted_by_time = list(reversed(sorted(related_articles,
                                                  key=lambda a: a.pub_time)))

            # Select above 50% articles sorted by topic probability
            num_articles = len(sorted_by_time)

            # Search position of publisher's article
            publisher_index = int(num_articles / 2)
            for i, a in enumerate(sorted_by_time):
                # Published id (Reuter Editorial) is 1
                if a.author.id == Rating.PUBLISHER_ID:
                    publisher_index = i
                    break

            # Sorted by latest -> old articles
            for i, s in enumerate(sorted_by_time):
                ret[s.author.id] += np.tanh((i - publisher_index) / num_articles)
                author_articles[s.author.id] += 1
                if s.author.id == Rating.PUBLISHER_ID:
                    print("XXXXX")
                    print(s.author.id)
                    print(s.author.name)
                    print(ret[s.author.id])
                    print(author_articles[s.author.id])

        # Make rating in average
        for k, v in ret.items():
            if author_articles[k] != 0:
                ret[k] = v / np.log(author_articles[k] + 1.0)

        self.rating = ret
        return self.rating

    def get_author_rate(self, author_id):
        return self.rating.get(author_id, 0.0)
