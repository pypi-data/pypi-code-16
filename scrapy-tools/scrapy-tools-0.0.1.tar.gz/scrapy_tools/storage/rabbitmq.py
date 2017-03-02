# -*- coding:utf-8 -*-
from scrapy import signals
import traceback
from scrapy.exceptions import NotConfigured
import logging
import pika
import sys
import time
import json

logger = logging.getLogger(__name__)
from datetime import datetime


class RabbitMQSignal():
    def __init__(self, crawler):
        crawler.signals.connect(self.item_scraped, signal=signals.item_scraped)
        crawler.signals.connect(self.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(self.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(self.spider_error, signal=signals.spider_error)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def item_scraped(self, item, spider):
        map = {}
        for key, val in item.items():
            if isinstance(val, datetime):
                map[key] = val.strftime('%Y-%m-%d %H:%M:%S')
            else:
                map[key] = val
        self.channel.basic_publish(exchange='',
                                   routing_key='crawler',
                                   body=json.dumps(map),
                                   properties=pika.BasicProperties(delivery_mode=2, ))
        print 'from rabbitmq signal:%s' % (json.dumps(map))

    def spider_opened(self, spider):
        con = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = con.channel()
        result = self.channel.queue_declare(queue='crawler', durable=True, exclusive=False)
        # pub/sub模式
        self.channel.exchange_declare(durable=False, exchange='mq_publish', type='fanout', )
        self.channel.queue_bind(exchange='mq_publish', queue=result.method.queue, routing_key='', )

    def spider_closed(self, spider, reason):
        self.channel.close()

    def spider_error(self, failure, response, spider):
        self.channel.close()


