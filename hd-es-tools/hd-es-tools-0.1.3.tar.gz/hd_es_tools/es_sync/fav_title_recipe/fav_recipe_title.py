# -*- coding: UTF-8 -*-
#
# @author huangyue<huangyue@haodou.com>
# @since 17/2/15
#

try:
    import elasticsearch
except ImportError:
    raise ImportError(
        "Error: elasticsearch (https://pypi.python.org/pypi/elasticsearch) "
        "version 2.x or 5.x is not installed.\n"
        "Install with:\n"
        "  pip install elastic-doc-manager[elastic2]\n"
        "or:\n"
        "  pip install elastic-doc-manager[elastic5]\n"
    )

from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan

es = Elasticsearch("http://10.0.10.200:9200/")
es2 = Elasticsearch("http://10.0.10.75:9200/")

count = 631630
curr = 100.0


def updateFav(msg):
    data = {
        "script": {
            "lang": "groovy",
            "stored": "fav-add-title",
            "params": {
                "objTitle": None,
                "objPinYin": None,
                "objSimPinYin": None,
            }
        },
        "query": {
            "bool": {
                "must": [
                    {
                        "term": {
                            "objId": "%s" % msg['_id']
                        }
                    }
                ],
                "must_not": [],
                "should": []
            }
        }
    }

    data['script']['params']['objTitle'] = msg['_source'].get('title');
    data['script']['params']['objPinYin'] = msg['_source'].get('pinYin');
    data['script']['params']['objSimPinYin'] = msg['_source'].get('simPinYin2');

    print "--data %.2f% %s" % (curr / count) % data
    try:
        res = es2.update_by_query("fav", "fav", data, wait_for_completion=True, timeout="1m", search_timeout="1m")
        print "--result %s" % res
    except Exception as exc:
        print "--error %s" % exc


for e in scan(es,
              query=None,
              index="hd04",
              doc_type="msg",
              scroll='10m',
              _source=True):
    curr += 100.0
    if e.get("_source", {}).get("title", None) is not None:
        updateFav(e)
