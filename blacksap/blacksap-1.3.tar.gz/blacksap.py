#!/usr/bin/env python
# coding=utf-8
""" Watch Torrent RSS feeds and download new torrent files.
"""
from __future__ import print_function
from collections import namedtuple
from functools import partial
from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool
import click
import feedparser
import hashlib
import json
import os
import requests
import sys
import time

__author__ = 'Jesse Almanrode (jesse@almanrode.com)'
__cfgfile__ = '~/.blacksap.cfg'
debug = False
config = None
http_header = {'user-agent': "Mozilla/5.0"}
RSSFeed = namedtuple('RSSFeed', ['data', 'hash'])


class BSError(Exception):
    """ blacksap error class
    """


class BSTimer(object):
    """ Class to time certain operations
    """

    def __init__(self):
        self.start_time = None
        self.stop_time = None
        self.delta = None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def start(self):
        """ Star the timer
        """
        self.start_time = time.time()

    def stop(self):
        """ Stop the timer
        """
        self.stop_time = time.time()
        self.delta = format(float(self.stop_time - self.start_time), '.4f')


def _blacksap(destination, reverse, count, feed):
    """ Private function which allows run sub-command to be threaded

    :param destination: Path to destination directory for torrent files
    :param reverse: Reverse RSS feed data before downloading torrents
    :param count: Limit the number of torrent files to download
    :param feed: Feed Config
    :return: Feed config
    """
    try:
        rss = download_rss_feed(feed['url'])
    except BSError as err:
        if debug:
            print(err)
        click.echo(feed['name'] + ': Unable to update RSS', err=True)
        return feed

    if feed['new'] and count == -1:
        count = 1
        feed['new'] = False

    if count == -1 and feed['hash'] == rss.hash:
        click.echo(feed['name'] + ': No new torrent files')
    else:
        feed['hash'] = rss.hash  # Update the hash now that we've checked it
        entries = rss.data['entries']
        downloaded_torrents = list()
        if reverse:
            entries = reversed(entries)
        if count == 0:
            entries = list()
        elif count > 0:
            entries = entries[0:count]
        for torrent in entries:
            try:
                torrent_name = torrent['torrent_filename']
            except KeyError:
                torrent_name = torrent['title']
            if count == -1 and torrent_name == feed['last']:
                break
            else:
                torrent_url = [x['href'] for x in torrent['links'] if x['type'] == 'application/x-bittorrent'].pop()
                if torrent_name not in downloaded_torrents:
                    try:
                        download_torrent_file(torrent_url, destination, torrent_name)
                        downloaded_torrents.append(torrent_name)
                    except BSError as err:
                        if debug:
                            print(err)
                        continue
        if len(downloaded_torrents) == 0:
            click.echo(feed['name'] + ': No new torrent files')
        else:
            click.echo(feed['name'] + ': downloaded ' + str(len(downloaded_torrents)) + ' torrents')
            if reverse:
                feed['last'] = downloaded_torrents.pop()
            else:
                feed['last'] = downloaded_torrents[0]
    return feed


def download_torrent_file(url, destination, filename):
    """Attempt to download a torrent file to a destination

    :param url: URL of torrent file
    :param destination: POSX path to output location
    :param filename: Name of the output file
    :return: True on file write
    :raises: BSError
    """
    global http_header
    if filename.endswith('.torrent') is False:
        filename += '.torrent'
    if url.startswith('http') is False:
        raise BSError('Not a url', url)
    if '?' in url:
        url = str(url.split('?')[0])
    rdata = requests.get(url, headers=http_header)
    if rdata.status_code != 200:
        raise BSError(rdata.status_code, rdata.reason)
    else:
        filename = filename.replace('/', '_')
        with open(destination + filename, 'wb') as tf:
            tf.write(rdata.content)
        return True


def download_rss_feed(url):
    """ Download an RSS feed and parse the contents.  Follows Redirects.

    :param url: URL to RSS feed
    :return: NamedTuple(data, hash)
    :raises: BSError
    """
    global http_header
    if url.startswith('http') is False:
        raise BSError('Not a url', url)
    try:
        rdata = requests.get(url, headers=http_header, timeout=5)
    except requests.exceptions.Timeout:
        raise BSError('Download timed out')
    if rdata.status_code != 200:
        raise BSError(rdata.status_code, rdata.reason)
    if rdata.url != url:
        return download_rss_feed(rdata.url)
    else:
        return RSSFeed(data=feedparser.parse(rdata.text), hash=hashlib.md5(rdata.text.encode('utf-8')).hexdigest())


@click.group()
@click.version_option()
@click.option('--debug', '-d', is_flag=True, help='Enable debug output')
def cli(**kwargs):
    """ Track torrent RSS feeds and download torrent files
    """
    global debug, config, __cfgfile__
    debug = kwargs['debug']
    __cfgfile__ = os.path.expanduser(__cfgfile__)
    if os.path.exists(__cfgfile__):
        with open(__cfgfile__) as fp:
            config = json.load(fp)
    else:
        config = {'feeds': list()}


@cli.command('track')
@click.option('--name', '-N', help='Name for RSS Feed')
@click.argument('url', required=True)
def cli_track(**kwargs):
    """ Track a new RSS feed
    """
    global debug, config, __cfgfile__
    for feed in config['feeds']:
        if kwargs['url'] == feed['url']:
            click.echo('Already tracking: ' + feed['name'])
            break
    else:
        try:
            rss_feed, rss_hash = download_rss_feed(kwargs['url'])
        except requests.HTTPError as err:
            if debug:
                print(err)
            click.echo('Unable to download: ' + kwargs['url'], err=True)
            sys.exit(1)
        feed = {'url': kwargs['url'],
                'name': rss_feed['feed']['title'],
                'hash': rss_hash,
                'new': True,
                'last': None}
        if kwargs['name']:
            feed['name'] = kwargs['name']
        config['feeds'].append(feed)
        with open(__cfgfile__, 'w') as fp:
            json.dump(config, fp, indent=2)
        click.echo('Added RSS feed: ' + feed['name'])
    sys.exit(0)


@cli.command('untrack')
@click.argument('url', required=True)
def cli_untrack(**kwargs):
    """ Stop tracking an RSS feed
    """
    global debug, config, __cfgfile__
    if len(config['feeds']) == 0:
        click.echo('Zero feeds tracked', err=True)
        sys.exit(0)
    newfeeds = list()
    for feed in config['feeds']:
        if feed['url'] != kwargs['url']:
            newfeeds.append(feed)
        else:
            click.echo('Untracked RSS feed: ' + feed['name'])
    if len(newfeeds) == len(config['feeds']):
        click.echo('Not being tracked: ' + kwargs['url'], err=True)
    config['feeds'] = newfeeds
    with open(__cfgfile__, 'w') as fp:
        json.dump(config, fp, indent=2)
    sys.exit(0)


@cli.command('tracking')
def cli_tracking():
    """ List tracked RSS feeds
    """
    global debug, config
    if len(config['feeds']) == 0:
        click.echo('Zero feeds tracked', err=True)
        sys.exit(0)
    totalfeeds = len(config['feeds'])
    click.echo('Total RSS feeds tracked: ' + str(totalfeeds))
    for feed in config['feeds']:
        click.echo('-' * 16)
        click.echo(feed['name'])
        click.echo('-' * 16)
        click.echo('URL: ' + feed['url'])
        click.echo('Last Torrent: ' + str(feed['last']))
    sys.exit(0)


@cli.command('run', short_help='Run blacksap on all tracked feeds')
@click.option('--reverse', '-R', is_flag=True, help='Read the feeds in reverse order (oldest to newest)')
@click.option('--count', '-c', default=-1, type=int, help='Number of torrent files to download')
@click.option('--output', '-o', type=click.Path(exists=True, file_okay=False, writable=True), required=True,
              help='Output directory for torrent files')
@click.argument('url', nargs=-1)
def cli_run(**kwargs):
    """ Update all RSS feeds and download new torrent files to output directory

    If count == -1 then all new torrent files will be downloaded.  If it is set to a non-zero
    number then exactly that many torrent files will be downloaded from each feed tracked regardless
    whether they are new in the feed or not.

    If url is specified, only the url of the feed specified will be updated. This url must already be
    tracked by blacksap!
    """
    global debug, config, __cfgfile__
    if len(config['feeds']) == 0:
        click.echo('Zero feeds tracked', err=True)
        sys.exit(0)

    if kwargs['output'].endswith('/') is False:
        kwargs['output'] += '/'

    if len(kwargs['url']) == 0:
        feeds = config['feeds']
    else:
        feeds = list()
        for url in kwargs['url']:
            for feed in config['feeds']:
                if url == feed['url']:
                    feeds.append(feed)
                    break
            else:
                click.echo('Feed not tracked: ' + url, err=True)
        if len(feeds) == 0:
            click.echo('Zero feeds to update')
            sys.exit(0)

    timer = BSTimer()
    timer.start()
    bspool = ThreadPool(processes=cpu_count())
    bsfunc = partial(_blacksap, kwargs['output'], kwargs['reverse'], kwargs['count'])
    feeds_updated = bspool.map(bsfunc, feeds)
    if len(feeds_updated) == config['feeds']:
        config['feeds'] = feeds_updated
    else:
        for idx, feed in enumerate(config['feeds']):
            for update in feeds_updated:
                if update['url'] == feed['url']:
                    config['feeds'][idx] = update
                    break
    with open(__cfgfile__, 'w') as fp:
        json.dump(config, fp, indent=2)
    timer.stop()
    click.echo(str(len(feeds)) + ' feeds checked in ' + str(timer.delta) + ' seconds')
    sys.exit(0)


if __name__ == '__main__':
    cli()
