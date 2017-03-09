# -*- coding: utf-8 -*-

import logging
import time

import dateutil.parser
import feedparser
import transaction
from oe_daemonutils.circuit import DaemonCircuitBreaker
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension


def date_from_string(s):
    d = dateutil.parser.parse(s)
    return d


class DaemonController(object):
    def __init__(self, settings, oauth_helper, daemon_manager_class, daemon_processor_class,
                 feed_endpoint=None, number_of_runs=1, retry_break=0):
        """
        Initialize the daemon feed controller given a daemon manager and a daemon processor

        :param settings: general configuration settings
        :param oauth_helper: authorization helper to get the system token
        :param daemon_manager_class: data manager class to get and update the latest feed entry id
        :param daemon_processor_class: processor class to process a feed entry
        :param feed_endpoint: provide a custom feed endpoint (not from teh standard 'daemon.feed.endpoint' setting)
        :param retry: the couples of times the daemon should run including stopping by failure
        :param retry_break: the time in seconds after failure the daemon should wait until it tries again
        """
        self.feed_endpoint = feed_endpoint if feed_endpoint else settings['daemon.feed.endpoint']
        self.number_of_runs = number_of_runs
        self.retry_break = retry_break
        # logging
        self.logger = logging.getLogger(settings['daemon.logger.name'])

        engine = engine_from_config(settings, 'sqlalchemy.')
        self.session_maker = sessionmaker(
            bind=engine,
            extension=ZopeTransactionExtension()
        )

        self.system_token = oauth_helper.get_system_token()
        self.processor = daemon_processor_class(settings, self.logger, self.system_token)
        self.daemon_manager_class = daemon_manager_class
        self.daemon_manager = None

    def parse_feed(self, feed_endpoint):
        """
        Parse the feed given the feed endpoint

        :rtype : Feed object
        """

        feed = feedparser.parse(feed_endpoint, request_headers={'OpenAmSSOID': self.system_token})
        summary = feed.feed.summary if 'summary' in feed.feed else ''
        if not hasattr(feed, 'status'):
            ex = feed.get('bozo_exception', {})
            self.logger.error('Unknown Error for url: ')
            self.logger.error(feed_endpoint)
            self.logger.error("{0} {1}".format(ex.__class__.__name__, ex.message))
            raise IOError('Unknown Error for url: {0}'.format(feed_endpoint), ex)
        elif 400 <= feed.status < 500:
            self.logger.error(feed.status)
            self.logger.error('Client Error for url: ')
            self.logger.error(feed_endpoint)
            self.logger.error(summary)
            raise IOError('Client Error for url: {0}'.format(feed_endpoint))
        elif 500 <= feed.status < 600:
            self.logger.error(feed.status)
            self.logger.error('Server Error for url: ')
            self.logger.error(feed_endpoint)
            self.logger.error(summary)
            raise IOError('Server Error for url: {0}'.format(feed_endpoint))
        else:
            return feed

    def process_entries(self, entries, last_entry_ts):
        """
        Process the given entries and adapt the latest processed entry id

        :param entries: current feed entries to process
        :param last_entry_ts: the latest entry id
        """
        for entry in entries:
            current_entry_ts = entry.updated
            process_uri = next(
                (link['href'] for link in entry.links if link['rel'] == 'related' and link['title'] == 'proces'), None)
            if not process_uri:
                self.logger.error('Entry {0} has no process!'.format(entry.id))
            else:
                self.processor.process_entry(entry)
            current = last_entry_ts
            last_entry_ts = current_entry_ts if current_entry_ts is not None else last_entry_ts
            with transaction.manager as manager:
                self.daemon_manager.update_last_entry_id(current=current, last=last_entry_ts)
                manager.commit()

    def process_previous_feed(self, feed, last_entry_ts):
        """
        Check if the entries of the previous feed must be processed

        :param feed: current feed
        :param last_entry_ts: last processed entry id
        :return:
        """
        entries = []
        previous_endpoint = next((link['href'] for link in feed.feed.links if link['rel'] == 'prev-archive'), None)
        if previous_endpoint:
            previous_feed = self.parse_feed(previous_endpoint)
            entries = self.process_feed(previous_feed, last_entry_ts)
        return entries

    def process_feed(self, feed, last_entry_ts):
        """
        Get the entries of the current that are not yet processed

        :param feed: current feed
        :param last_entry_ts: last processed entry id
        :return:
        """
        entries = []
        first_ts = date_from_string(feed.entries[0].updated) if len(feed.entries) > 0 else None
        if first_ts is None:
            entries.extend(self.process_previous_feed(feed, last_entry_ts))
        elif first_ts and last_entry_ts is None:
            entries = feed.entries
        elif first_ts and first_ts <= last_entry_ts:
            entries = [entry for entry in feed.entries if date_from_string(entry.updated) > last_entry_ts]
        elif first_ts and first_ts > last_entry_ts:
            entries.extend(self.process_previous_feed(feed, last_entry_ts))
            entries.extend(feed.entries)
        return entries

    def run_daemon(self):
        """
        check the feed and process new items
        """
        session = self.session_maker()
        try:
            self.daemon_manager = self.daemon_manager_class(session)
            last_entry_ts = self.daemon_manager.retrieve_last_entry_id()
            last_entry_ts_datetime = date_from_string(last_entry_ts) if last_entry_ts else None
            circuit = DaemonCircuitBreaker(self.parse_feed, self.logger, (IOError, ValueError))
            feed = circuit.call(self.feed_endpoint)

            if feed:
                entries_to_process = self.process_feed(feed, last_entry_ts_datetime)
                self.process_entries(entries_to_process, last_entry_ts)
        finally:
            if self.processor.notifications_dict and len(self.processor.notifications_dict) > 0:
                self.processor.notify()
            session.close()

        time.sleep(1)

    def run(self):  # pragma: no cover
        """
        run the daemon indefinitely
        """
        self.logger.info('daemon started')
        try:
            while True:
                self.run_daemon()
        except (KeyboardInterrupt, SystemExit):
            self._handle_manual_stop()
        except Exception as e:
            self._handle_unrecoverable_error(e)

    def _handle_manual_stop(self):
        self.logger.warn('manual stop')
        self.logger.warn('daemon stopped')

    def _handle_unrecoverable_error(self, ex):
        self.logger.warn('unrecoverable error')
        self.logger.error(ex)
        self.logger.warn('daemon stopped')
        raise ex
