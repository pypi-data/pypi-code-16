#!/usr/bin/env python

import argparse
import logging
import os
import sys

import sqlalchemy

from .metrics import optityper_result

def get_param(args, param_name):
    if vars(args)[param_name] == None:
        return None
    else:
        return vars(args)[param_name]
    return

def setup_logging(tool_name, args, run_uuid):
    logging.basicConfig(
        filename=os.path.join(uuid + '_' + tool_name + '.log'),
        level=args.level,
        filemode='w',
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d_%H:%M:%S_%Z',
    )
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    logger = logging.getLogger(__name__)
    return logger

def main():
    parser = argparse.ArgumentParser('picard docker tool')

    # Logging flags.
    parser.add_argument('-d', '--debug',
        action = 'store_const',
        const = logging.DEBUG,
        dest = 'level',
        help = 'Enable debug logging.',
    )
    parser.set_defaults(level = logging.INFO)

    # Required flags.
    parser.add_argument('--gdc_uuid',
                        required = True
    )
    parser.add_argument('--metric_path',
                        required = True
    )
    parser.add_argument('--run_uuid',
                        required = True
    )

    # setup required parameters
    args = parser.parse_args()
    gdc_uuid = args.gdc_uuid
    metric_path = args.metric_path
    run_uuid = args.run_uuid

    logger = setup_logging('optityper_result', args, run_uuid)

    sqlite_name = run_uuid + '.db'
    engine_path = 'sqlite:///' + sqlite_name
    engine = sqlalchemy.create_engine(engine_path, isolation_level='SERIALIZABLE')

    optityper_result.run(gdc_uuid, metric_path, run_uuid, engine, logger)

    return

if __name__ == '__main__':
    main()
