#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse
import time

from statsd import StatsClient
import mongo_statsd


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', help='stat name', action='store')
    parser.add_argument('--statsd_host', help='statsd host', action='store')
    parser.add_argument('--statsd_port', default=8125, type=int, help='statsd port', action='store', required=False)
    parser.add_argument('--mongodb_host', help='mongodb host', action='store', required=False)
    parser.add_argument('--mongodb_port', type=int, help='mongdb port', action='store', required=False)
    parser.add_argument('--mongodb_username', help='mongodb username', action='store', required=False)
    parser.add_argument('--mongodb_password', help='mongodb password', action='store', required=False)
    parser.add_argument('-v', '--version', action='version', version='%s' % mongo_statsd.__version__)

    return parser


def run():
    args = build_parser().parse_args()

    statsd_client = StatsClient(args.statsd_host, args.statsd_port)

    stat_reporter = mongo_statsd.StatReporter(statsd_client, args.name,
                                              args.mongodb_host, args.mongodb_port,
                                              args.mongodb_username, args.mongodb_password,
                                              )

    while True:

        stat_reporter.report()

        try:
            time.sleep(1)
        except KeyboardInterrupt:
            sys.exit(0)

if __name__ == '__main__':
    run()

