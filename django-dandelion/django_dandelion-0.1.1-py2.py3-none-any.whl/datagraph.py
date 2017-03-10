# -*- coding: utf-8

from __future__ import unicode_literals

from .base import BaseDandelionParamsRequest


class Wikisearch(BaseDandelionParamsRequest):
    """
    Looking for Wikipedia pages but don't know their exact title? We can help you to search for the page you want.
    You can also test Wikisearch from the demo page, at wikisearch.dandelion.eu

    https://dandelion.eu/docs/api/datagraph/wikisearch/
    """

    def __init__(self, **params):
        """
        :param params:
            text = A string that you want to be matched against Wikipedia.
                | required
                | Type: string
                | Example: text=tower of big ben
            lang = The language of the string to be searched; currently English, French, German, Italian, Portuguese
                and Spanish are supported.
                | required
                | Type: string
                | Default value: en
                | Accepted values: de | en | es | fr | it | pt
            limit = Restricts the output to the first N results.
                | optional
                | Type: integer
                | Default value: 10
                | Accepted values: 1 .. 50
            offset = Starts listing the results from the given index. Mostly used in combination with limit parameter,
                for pagination purposes.
                | optional
                | Type: integer
                | Default value: 0
            query = With this parameter you can choose the behaviour of the search.
                If you want to search for all the entities that:
                - contain the text: use full;
                - start with the text: use prefix
                The prefix option is very useful in autocomplete scenarios.
                | optional
                | Type: string
                | Default value: full
                | Accepted values: full | prefix
            include = Returns more information on annotated entities:
                - "types" adds type information from DBpedia or dandelion. DBpedia types are extracted based on the
                  lang parameter (e.g. if lang=en, types are extracted from DBpedia english).
                  Please notice that different DBpedia instances may contain different types for the same resource;
                - "categories" adds category information from DBpedia/Wikipedia;
                - "abstract" adds the text of the Wikipedia abstract;
                - "image" adds a link to an image depicting the tagged entity, as well as a link to the image
                  thumbnail, served by Wikipedia. Please check the licensing terms of each image on Wikipedia before
                  using it in your app;
                - "lod" adds links to equivalent (sameAs) entities in Linked Open Data repositories or other websites.
                  It currently only supports DBpedia and Wikipedia;
                - "alternate_labels" adds some other names used when referring to the entity.
                | optional
                | Type: comma-separated list
                | Default value: <empty string>
                | Accepted values: types, categories, abstract, image, lod, alternate_labels
                | Example: include=types,lod
        """

        keys_allowed = [
            'text',
            'lang',
            'limit',
            'offset',
            'query',
            'include',
        ]

        super(Wikisearch, self).__init__(keys_allowed=keys_allowed, keys_unique=[[]], **params)

    def analyze(self):
        return self._do_request(
            extra_url=('datagraph', 'wikisearch', 'v1'),
            method='post'
        )
