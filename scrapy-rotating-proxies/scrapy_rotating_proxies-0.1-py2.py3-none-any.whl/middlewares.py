# -*- coding: utf-8 -*-
from __future__ import absolute_import
import logging
from functools import partial
from six.moves.urllib.parse import urlsplit

import scrapy
from scrapy.exceptions import CloseSpider, NotConfigured
from scrapy import signals
from scrapy.utils.url import add_http_if_no_scheme
from twisted.internet import task

from .expire import Proxies, exp_backoff_full_jitter


logger = logging.getLogger(__name__)


class RotatingProxyMiddleware(object):
    """
    Scrapy downloader middleware which choses a random proxy for each request.

    To enable it, add it and BanDetectionMiddleware
    to DOWNLOADER_MIDDLEWARES option::

        DOWNLOADER_MIDDLEWARES = {
            # ...
            'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
            'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
            # ...
        }

    It keeps track of dead and alive proxies and avoids using dead proxies.
    Proxy is considered dead if request.meta['_ban'] is True, and alive
    if request.meta['_ban'] is False; to set this meta key use
    BanDetectionMiddleware.

    Dead proxies are re-checked with a randomized exponential backoff.

    By default, all default Scrapy concurrency options (DOWNLOAD_DELAY,
    AUTHTHROTTLE_..., CONCURRENT_REQUESTS_PER_DOMAIN, etc) become per-proxy
    for proxied requests when RotatingProxyMiddleware is enabled.
    For example, if you set CONCURRENT_REQUESTS_PER_DOMAIN=2 then
    spider will be making at most 2 concurrent connections to each proxy.

    Settings:

    * ``ROTATING_PROXY_LIST``  - a list of proxies to choose from;
    * ``ROTATING_PROXY_LOGSTATS_INTERVAL`` - stats logging interval in seconds,
      30 by default;
    * ``ROTATING_PROXY_CLOSE_SPIDER`` - When True, spider is stopped if
      there are no alive proxies. If False (default), then when there is no
      alive proxies all dead proxies are re-checked.
    * ``ROTATING_PROXY_PAGE_RETRY_TIMES`` - a number of times to retry
      downloading a page using a different proxy. After this amount of retries
      failure is considered a page failure, not a proxy failure. Default: 15.
    * ``ROTATING_PROXY_BACKOFF_BASE`` - base backoff time, in seconds.
      Default is 300 (i.e. 5 min).
    """
    def __init__(self, proxy_list, logstats_interval, stop_if_no_proxies,
                 max_page_retry_times, backoff_base):

        backoff = partial(exp_backoff_full_jitter, base=backoff_base)
        self.proxies = Proxies(self.cleanup_proxy_list(proxy_list),
                               backoff=backoff)
        self.logstats_interval = logstats_interval
        self.reanimate_interval = 5
        self.stop_if_no_proxies = stop_if_no_proxies
        self.max_page_retry_times = max_page_retry_times

    @classmethod
    def from_crawler(cls, crawler):
        s = crawler.settings
        proxy_list = s.getlist('ROTATING_PROXY_LIST')
        if not proxy_list:
            raise NotConfigured()
        mw = cls(
            proxy_list=proxy_list,
            logstats_interval=s.getfloat('ROTATING_PROXY_LOGSTATS_INTERVAL', 30),
            stop_if_no_proxies=s.getbool('ROTATING_PROXY_CLOSE_SPIDER', False),
            max_page_retry_times=s.getint('ROTATING_PROXY_PAGE_RETRY_TIMES', 10),
            backoff_base=s.getfloat('ROTATING_PROXY_BACKOFF_BASE', 300)
        )
        crawler.signals.connect(mw.engine_started,
                                signal=signals.engine_started)
        crawler.signals.connect(mw.engine_stopped,
                                signal=signals.engine_stopped)
        return mw

    def engine_started(self):
        self.log_task = task.LoopingCall(self.log_stats)
        self.log_task.start(self.logstats_interval, now=True)
        self.reanimate_task = task.LoopingCall(self.reanimate_proxies)
        self.reanimate_task.start(self.reanimate_interval, now=False)

    def reanimate_proxies(self):
        n_reanimated = self.proxies.reanimate()
        if n_reanimated:
            logger.debug("%s proxies moved from 'dead' to 'reanimated'",
                         n_reanimated)

    def engine_stopped(self):
        if self.log_task.running:
            self.log_task.stop()
        if self.reanimate_task.running:
            self.reanimate_task.stop()

    def process_request(self, request, spider):
        if 'proxy' in request.meta and not request.meta.get('_rotating_proxy'):
            return
        proxy = self.proxies.get_random()
        if not proxy:
            if self.stop_if_no_proxies:
                raise CloseSpider("no_proxies")
            else:
                logger.warn("No proxies available; marking all proxies "
                            "as unchecked")
                self.proxies.reset()
                proxy = self.proxies.get_random()
                if proxy is None:
                    logger.error("No proxies available even after a reset.")
                    raise CloseSpider("no_proxies_after_reset")

        request.meta['proxy'] = proxy
        request.meta['download_slot'] = self.get_proxy_slot(proxy)
        request.meta['_rotating_proxy'] = True

    def get_proxy_slot(self, proxy):
        """
        Return downloader slot for a proxy.
        By default it doesn't take port in account, i.e. all proxies with
        the same hostname / ip address share the same slot.
        """
        # FIXME: an option to use website address as a part of slot as well?
        return urlsplit(proxy).hostname

    def process_exception(self, request, exception, spider):
        return self._handle_result(request, spider)

    def process_response(self, request, response, spider):
        return self._handle_result(request, spider) or response

    def _handle_result(self, request, spider):
        proxy = request.meta.get('proxy', None)
        if not (proxy and request.meta.get('_rotating_proxy')):
            return
        ban = request.meta.get('_ban', None)
        if ban is True:
            self.proxies.mark_dead(proxy)
            return self._retry(request, spider)
        elif ban is False:
            self.proxies.mark_good(proxy)

    def _retry(self, request, spider):
        retries = request.meta.get('proxy_retry_times', 0) + 1

        if retries <= self.max_page_retry_times:
            logger.debug("Retrying %(request)s with another proxy "
                         "(failed %(retries)d times)",
                         {'request': request, 'retries': retries},
                         extra={'spider': spider})
            retryreq = request.copy()
            retryreq.meta['proxy_retry_times'] = retries
            retryreq.dont_filter = True
            return retryreq
        else:
            logger.debug("Gave up retrying %(request)s (failed %(retries)d "
                         "times with different proxies)",
                         {'request': request, 'retries': retries},
                         extra={'spider': spider})

    def log_stats(self):
        logger.info('%s' % self.proxies)

    @classmethod
    def cleanup_proxy_list(cls, proxy_list):
        lines = [line.strip() for line in proxy_list]
        return list({
            add_http_if_no_scheme(url)
            for url in lines
            if url and not url.startswith('#')
        })


class BanDetectionMiddleware(object):
    """
    Downloader middleware for detecting bans. It adds
    '_ban': True to request.meta if the response was a ban.

    To enable it, add it to DOWNLOADER_MIDDLEWARES option::

        DOWNLOADER_MIDDLEWARES = {
            # ...
            'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
            # ...
        }

    By default, client is considered banned if a request failed, and alive
    if a response was received. This can be overridden in a spider using
    ``response_is_ban`` and ``exception_is_ban`` spider methods, for
    example::

        class MySpider(scrapy.spider):
            # ...

            def response_is_ban(self, request, response):
                return b'banned' in response.body

            def exception_is_ban(self, request, exception):
                return None

    These methods can return True (ban detected), False (not a ban) or
    None (unknown).
    """
    def process_response(self, request, response, spider):
        ban = (response.status != 200) or (not len(response.body))
        if hasattr(spider, 'response_is_ban'):
            ban = spider.response_is_ban(request, response)
        request.meta['_ban'] = ban
        return response

    def process_exception(self, request, exception, spider):
        ban = True
        if hasattr(spider, 'exception_is_ban'):
            ban = spider.exception_is_ban(request, exception)
        request.meta['_ban'] = ban
