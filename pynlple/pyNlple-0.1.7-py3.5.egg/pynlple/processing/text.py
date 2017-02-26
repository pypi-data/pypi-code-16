# -*- coding: utf-8 -*-


class TokenFilter(object):

    def filter(self, tokens):
        """
        Filter out tokens according to specific rules.

        :param list tokens: string list of tokens to filter
        :return: filtered list of tokens
        :rtype: list
        """
        return None


class ClassTokenFilter(TokenFilter):

    def __init__(self, tagger, filtered_classes=None):
        self.__tagger = tagger
        self.filtered_classes = filtered_classes

    def filter(self, tokens):
        tags = self.__tagger.get_tagged_entities(tokens, all_=False)
        if self.filtered_classes:
            tags = filter(lambda t: t[2] in self.filtered_classes, tags)
        valid_ids = sorted(set(range(0, len(tokens))) - {i for start, end, _ in tags for i in range(start, end)})
        return [tokens[i] for i in valid_ids]
