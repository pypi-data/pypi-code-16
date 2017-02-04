# -*- coding: utf-8 -*-
"""
文書と文の各データベース用のマネージャー
"""

import math
from elasticsearch_manager import ElasticsearchManager


class PatternManager(ElasticsearchManager):

    def __init__(self, host="localhost:9200"):
        ElasticsearchManager.__init__(self, host)
        self.index = "relretrieval"
        self.doc_type = "patterns"
        self.properties = {
            "relations": {
                "type": "nested",
                "properties": {
                    "BEF": {
                        "type": "string",
                        "store": "true",
                        "index": "analyzed",
                    },
                    "BET": {
                        "type": "string",
                        "store": "true",
                        "index": "analyzed",
                    },
                    "AFT": {
                        "type": "string",
                        "store": "true",
                        "index": "analyzed",
                    },
                    "tuples": {
                        "type": "nested",
                        "properties": {
                            "first": {
                                "type": "string",
                                "store": "true",
                                "index": "not_analyzed",
                            },
                            "second": {
                                "type": "string",
                                "store": "true",
                                "index": "not_analyzed",
                            },
                        },
                    },
                },
            },
        }

    def find_patters_by_query(self, query):
        should_words = [{"term": {"relations.%s" % key: value}} for key, value in query.items()]
        body = {
            "query": {
                "nested": {
                    "path": "relations",
                    "filter": {
                        "bool": {
                            "should": should_words
                        }
                    }
                }
            }
        }
        return self.search(body)


class SentenceManager(ElasticsearchManager):
    """
    文単位でのデータベースマネージャー

    プロパティの説明

        * article_id : 所属する文書のID
        * order : 所属する文書内での文の連続番号
        * tokens : ステミング済のトークンの配列
        * entities : 文に含まれるエンティティの情報

    """

    def __init__(self, host="localhost:9200"):
        ElasticsearchManager.__init__(self, host)
        # article と index を同じにした場合のメリットとデメリットは要調査
        self.index = "relretrieval"
        self.doc_type = "sentences"
        self.properties = {
            "article_id": {
                "type": "integer",
                "store": "true",
            },
            "order": {
                "type": "integer",
                "store": "false",
            },
            "tokens": {
                "type": "nested",
                "properties": {
                    "token": {
                        "type": "string",
                        "store": "true",
                        "index": "analyzed",
                    },
                },
            },
            "entities": {
                "type": "nested",
                "properties": {
                    "token_index": {
                        "type": "integer",
                        "store": "false",
                    },
                    "token": {
                        "type": "string",
                        "store": "true",
                        "index": "not_analyzed",
                    },
                    "label": {
                        "type": "string",
                        "store": "true",
                        "index": "not_analyzed",
                    },
                },
            },
        }

    def get_by_article_id(self, article_id, **kwargs):
        body = {
            "query": {
                "match": {
                    "article_id": article_id
                }
            }
        }
        body.update(kwargs)
        return self.search(body)

    def find_sentences_by_entities(self, entities):
        """
        This needs Javascript language plugin.

            ```
            path/to/elasticsearch/bin/plugin install lang-javascript
            ```
        """

        should_tokens = [{"term": {"entities.token": entity}} for entity in entities]
        body = {
            "query": {
                "nested": {
                    "path": "entities",
                    "filter": {
                        "bool": {
                            "should": should_tokens
                        }
                    }
                }
            },
            "filter": {
                "script": {
                    "script": {
                        "lang": "javascript",
                        "inline": "_source.entities.length > 1"
                    }
                }
            }
        }
        return self.search(body)

    def get_sentences_having_more_than_two_entities(self, size=10):
        # TODO
        # elasticsearchのページネーション的なやつのイテレータを返したい
        body = {
            "size": size,
            "filter": {
                "script": {
                    "script": {
                        "lang": "javascript",
                        "inline": "_source.entities.length > 1"
                    }
                }
            }
        }
        return self.search(body)
