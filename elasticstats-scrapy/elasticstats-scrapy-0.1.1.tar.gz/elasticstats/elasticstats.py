from datetime import datetime
import hashlib
import logging

from elasticsearch import Elasticsearch
from scrapy import signals
from scrapy.exceptions import NotConfigured


logger = logging.getLogger(__name__)


class ElasticStatsSender(object):

    def __init__(self, stats, settings):
        self.stats = stats
        self.settings = settings

    def _get_es_instance(self):
        settings = self.settings

        auth_type = settings.get('ELASTICSEARCH_AUTH')
        hosts = settings.getlist('ELASTICSEARCH_SERVERS')

        if auth_type == 'BASIC_AUTH':
            use_ssl = settings.getbool('ELASTICSEARCH_USE_SSL')
            auth_tuple = (settings.get('ELASTICSEARCH_USERNAME'),
                          settings.get('ELASTICSEARCH_PASSWORD'))
            if use_ssl:
                return Elasticsearch(hosts=hosts,
                                     http_auth=auth_tuple,
                                     port=443, use_ssl=True)
            else:
                return Elasticsearch(hosts=hosts,
                                     http_auth=auth_tuple)
        else:
            return Elasticsearch(hosts=hosts)

    @classmethod
    def from_crawler(cls, crawler):
        enabled = crawler.settings.getbool("ELASTICSTATS_ENABLED")
        if not enabled:
            raise NotConfigured

        o = cls(crawler.stats, crawler.settings)
        crawler.signals.connect(o.spider_closed, signal=signals.spider_closed)
        return o

    def spider_closed(self, spider):
        stats = {}

        index = self.settings.get('ELASTICSTATS_INDEX')
        doc_type = self.settings.get('ELASTICSTATS_TYPE')

        es = self._get_es_instance()
        stats['spider'] = spider.name
        stats['created_at'] = datetime.utcnow().isoformat()

        stats['stats'] = self.stats.get_stats()
        # stats['spider_stats'] = self.stats.get_stats(spider)

        # convert datetime objects into str
        for key, value in stats['stats'].iteritems():
            if isinstance(value, datetime):
                stats['stats'][key] = value.isoformat()
        try:
            doc_id = hashlib.sha1(stats['created_at']).hexdigest()
            return es.create(index=index, doc_type=doc_type, id=doc_id, body=stats)
        except Exception as e:
            logger.error('caught error while trying to send stats to elastic'
                         'Exception: {}'.format(e.message))
            logger.info('stats: {}'.format(stats))
