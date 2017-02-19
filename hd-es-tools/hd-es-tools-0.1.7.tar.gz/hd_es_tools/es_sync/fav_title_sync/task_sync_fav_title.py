# -*- coding: UTF-8 -*-
#
# @author huangyue<huangyue@haodou.com>
# @since 17/2/17
#

# -*- coding: UTF-8 -*-
#
# @author huangyue<huangyue@haodou.com>
# @since 17/2/16
#
import json
import urllib2
import datetime
import os
import sys
import logging
import logging.handlers
import time

SYNC_LOG_FORMAT = ('%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s')
LOG = logging.getLogger(__name__)

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

from elasticsearch import Elasticsearch, exceptions as es_exceptions, connection as es_connection
from elasticsearch.helpers import bulk, scan, streaming_bulk, BulkIndexError

SYNC_INTERAL = 10 * 60

dirname, filename = os.path.split(os.path.abspath(__file__))

SYNC_HOME = '/tmp/es/es_sync/fav_title_sync'
SYNC_DATA_HOME = SYNC_HOME + '/data/'
SYNC_LOG_HOME = SYNC_HOME + '/log/'

try:
    if not os.path.exists(SYNC_HOME):
        os.makedirs(SYNC_HOME)
    if not os.path.exists(SYNC_DATA_HOME):
        os.makedirs(SYNC_DATA_HOME)
    if not os.path.exists(SYNC_LOG_HOME):
        os.makedirs(SYNC_LOG_HOME)
except Exception as e:
    raise e

ES_HOST = ['elastic:changeme@10.0.10.71:9200', 'elastic:changeme@10.0.10.200:9200', 'elastic:changeme@10.0.10.201:9200']
ES_INDEX = 'hd01'
ES_INDEX_TYPE = 'fav'


class TaskSyncFavTitle(object):
    # 1 获取收藏标题
    # 2 保存失败的doc到文件
    # 3 从文件中重补全标题

    def __init__(self, es=None, docs=None, file=None):
        self.es = es
        self.docs = []
        self.file = None
        self.err = []

    def getFilePath(self, interal=0):
        times = int(time.time())
        startTime = times - times % SYNC_INTERAL + interal * SYNC_INTERAL;
        return "%s%s.data" % (SYNC_DATA_HOME, time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(startTime)))

    def getObj(self, doc):
        try:
            id = doc['objId']
            type = doc['objType']
            urls = {
                1: "http://10.100.1.49:8092/platform/msg/message/get.json?mid=%s",
                2: "http://10.100.1.49:8190/message/proxy/get.json?id=%s",
                3: "http://10.100.1.84:8091/interact/favorite/dir/get.json?ids=[\"%s\"]",
            }
            url = urls.get(type, None)
            if url is None:
                yield None, None, None

            url = url % id
            req = urllib2.Request(url)
            res_data = urllib2.urlopen(req, data=None, timeout=0.2)
            res = res_data.read()
            res_json = json.loads(res)
            data_json = res_json.get("data", None)

            if data_json is None:
                raise Exception('getObj error' + res)

            if isinstance(data_json, list):
                if len(data_json) > 0:
                    data_json = data_json[0]
                else:
                    pass

            if type == 1:
                yield data_json.get("title", None), None, None
            elif type == 2:
                yield data_json.get("title", None), data_json.get("pinYin", None), data_json.get("simPinYin", None)
            elif type == 3:
                yield data_json.get("title", None), None, None

        except Exception as e:
            LOG.error("getObj[%s]|error[%s]" % (json.dumps(doc), e))
            raise e

    def syncFromDocs(self):
        for doc in self.docs:
            try:
                for objTitle, objPinYin, objSimPinYin in self.getObj(doc):
                    if objTitle is not None:
                        data = {}
                        data['objTitle'] = objTitle
                        if objPinYin is not None:
                            data['objPinYin'] = objPinYin
                        if objSimPinYin is not None:
                            data['objSimPinYin'] = objSimPinYin
                        self.es.update(ES_INDEX, ES_INDEX_TYPE, doc["_id"], {"doc": data})
            except Exception as err:
                self.err.append(doc)

    # 保存到 SYNC_DATA_HOME
    # docs = [{"_id":"aaaaaaaaaaa","objId":"bbbbbbbbbb","objType":2},...]
    def saveErrorDoc(self, docs=[], file=None):
        try:
            if docs is None or len(docs) == 0:
                return

            error = ''
            for item in docs:
                if isinstance(item, str):
                    error += item + "\n"
                elif isinstance(item, dict):
                    error += "%s\n" % json.dumps(item)

            if len(error) > 0:
                if file is None:
                    file = self.getFilePath(0)
                LOG.info("--saveErrorDoc count[%s][%s]" % (len(self.docs), file))
                fp = open(file, 'a')
                fp.write(error)
                fp.close()
        except Exception as e:
            LOG.error("saveErrorDoc error:[%s][%s]" % (e, json.dumps(docs)))
            pass

    # SYNC_DATA_HOME sync
    def syncFromDefaultFile(self):
        LOG.info("--syncFromDefaultFile")
        self.file = self.getFilePath(-1)
        if os.path.isfile(self.file):
            try:
                fp = open(self.file, 'r+')
                for line in fp.readlines():
                    try:
                        if line == '\n':
                            continue
                        doc = json.loads(line)
                        self.docs.append(doc)
                    except Exception as err:
                        self.err.append(line)
                        LOG.error("doc[" + line + "]|error[%s]" % err)
                fp.close()
                os.remove(self.file)
                self.syncFromDocs()
            except Exception as err:
                pass
            self.saveErrorDoc(self.err, self.file)
        else:
            LOG.info("--syncFromDefaultFile no file %s", self.file)

    def sync(self):
        self.setup_logging()
        self.syncFromDefaultFile()

    def setup_logging(self):
        try:
            root_logger = logging.getLogger()
            formatter = logging.Formatter(SYNC_LOG_FORMAT)
            loglevel = logging.INFO
            root_logger.setLevel(loglevel)

            logfile = SYNC_LOG_HOME + 'sync_fav_title.log'

            log_out = logging.handlers.TimedRotatingFileHandler(
                logfile,
                when='D',
                interval=1,
                backupCount=0
            )
            print("Logging to %s." % logfile)

            log_out.setLevel(loglevel)
            log_out.setFormatter(formatter)
            root_logger.addHandler(log_out)
            return root_logger
            pass
        except Exception as e:
            raise e


def main():
    es = Elasticsearch(ES_HOST)
    sync = TaskSyncFavTitle(es)
    sync.sync()


if __name__ == '__main__':
    main()
