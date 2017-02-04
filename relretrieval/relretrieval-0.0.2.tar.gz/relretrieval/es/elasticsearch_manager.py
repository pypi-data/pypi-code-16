# -*- coding: utf-8 -*-
"""
Elasticsearch 関連の抽象クラスや共通メソッド
"""

from elasticsearch import Elasticsearch, helpers


def unicode_only_string(obj):
    # str の encode として utf-8 以外は想定していない
    return unicode(obj, "utf-8") if (isinstance(obj, str)) else obj


class ElasticsearchManager:
    """
    Elasticsearch ORM 用の抽象クラス
    elasticsearch モジュールのAPIに関しては http://elasticsearch-py.readthedocs.io/en/latest/api.html
    """

    settings_default = {
        "index": {
            "number_of_shards": 1,  # for termvectors
            "number_of_replicas": 0,
        },
        "analysis": {
            "analyzer": {
                "default_index": {
                    "type": "custom",
                    "tokenizer": "whitespace",
                    "filter": [
                        "lowercase",
                        "type_as_payload",
                    ],
                },
                "default_search": {
                    "type": "custom",
                    "tokenizer": "whitespace",
                    "filter": [
                        "lowercase",
                        "type_as_payload",
                    ],
                },
            },
        },
    }

    def __init__(self, host="localhost:9200", settings=None):
        """
        継承クラスでは `index`, `doc_type`, `properties` をインスタンス変数として定義する。

        例：

            self.index = "wikipedia-en-articles"
            self.doc_type = "wikipedia-en-articles-type"
            self.properties = {
                "title": {
                    "type": "string",
                    "store": "true",
                    "index": "analyzed",
                },
                "text": {
                    "type": "string",
                    "store": "true",
                    "index": "analyzed",
                    "term_vector": "with_positions_offsets",
                },
            }

        `properties` に関しては put_mapping に渡せるように定義する。
        https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-params.html

        """
        self.es = Elasticsearch(host)
        self.settings = settings if settings != None else self.settings_default

    def create_index(self):
        """
        インデックスを生成
        """
        body = {
            "settings": self.settings,
        }
        self.es.indices.create(index=self.index,  body=body)

    def put_mapping(self):
        """
        マッピングを設定
        """
        mapping = {
            self.doc_type: {
                "properties": self.properties,
            },
        }
        self.es.indices.put_mapping(index=self.index, doc_type=self.doc_type, body=mapping)

    def delete_index(self):
        """
        インデックスを削除
        """
        self.es.indices.delete(index=self.index)

    def refresh(self):
        """
        インデックスをリフレッシュ？
        """
        self.es.indices.refresh(index=self.index)

    def extract_properties(self, item):
        extracted = {k: item["_source"][k] for k in self.properties.keys()}
        extracted.update({"id": item["_id"]})
        return extracted

    def save(self, document):
        self.es.index(
            index=self.index,
            doc_type=self.doc_type,
            id=document.get("id", None),
            body={k: unicode_only_string(document[k]) for k in self.properties.keys()},
        )

    def bulk(self, documents):
        actions = [{"_index": self.index,
                    "_type": self.doc_type,
                    "_id": document["id"],
                    "_source": {k: unicode_only_string(document[k]) for k in self.properties.keys()},
                    } for document in documents]
        helpers.bulk(self.es, actions)

    def get(self, doc_id):
        return self.extract_properties(self.es.get(index=self.index, doc_type=self.doc_type, id=doc_id))

    def search(self, body):
        return [self.extract_properties(item)
                for item in self.es.search(index=self.index, doc_type=self.doc_type, body=body)["hits"]["hits"]]

    def doc_count(self):
        # 1384314139815 19:42:19 428
        return int(self.es.cat.count(index=self.index).split()[2])

    def termvectors(self, doc_id, fields=[]):
        fields = self.properties.keys()
        options = {
            "field_statistics": False,
            "offsets": False,
            "payloads": True,
            "positions": False,
            "term_statistics": True,
        }
        return self.es.termvectors(index=self.index, doc_type=self.doc_type, id=doc_id, fields=fields, **options)["term_vectors"]
