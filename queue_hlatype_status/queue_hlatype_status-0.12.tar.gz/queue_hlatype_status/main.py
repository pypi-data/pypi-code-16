#!/usr/bin/env python

import argparse
import datetime
import logging
import os
import time

import sqlalchemy
import pandas as pd

def setup_logging(args, uuid):
    logging.basicConfig(
        filename=os.path.join(uuid + '.log'),
        level=args.level,
        filemode='w',
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d_%H:%M:%S_%Z',
    )
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    logger = logging.getLogger(__name__)
    return logger

def main():
    parser = argparse.ArgumentParser('update status of job')
    # Logging flags.
    parser.add_argument('-d', '--debug',
        action = 'store_const',
        const = logging.DEBUG,
        dest = 'level',
        help = 'Enable debug logging.',
    )
    parser.set_defaults(level = logging.INFO)

    parser.add_argument('--gdc_uuid',
                        required=True
    )
    parser.add_argument('--hostname',
                        required=True
    )
    parser.add_argument('--host_ipaddress',
                        required=True
    )
    parser.add_argument('--host_mac',
                        required=True
    )
    parser.add_argument('--num_threads',
                        required=True
    )
    parser.add_argument('--repo',
                        required=True
    )
    parser.add_argument('--repo_hash',
                        required=True
    )
    parser.add_argument('--run_uuid',
                        required=True
    )
    parser.add_argument('--status',
                        required=True
    )
    parser.add_argument('--table_name',
                        required=True
    )

    args = parser.parse_args()

    gdc_uuid = args.gdc_uuid
    hostname = args.hostname
    host_ipaddress = args.host_ipaddress
    host_mac = args.host_mac
    num_threads = args.num_threads
    repo = args.repo
    repo_hash = args.repo_hash
    run_uuid = args.run_uuid
    status = args.status
    table_name = args.table_name

    logger = setup_logging(args, run_uuid)

    sqlite_name = run_uuid + '.db'
    engine_path = 'sqlite:///' + sqlite_name
    engine = sqlalchemy.create_engine(engine_path, isolation_level='SERIALIZABLE')

    datetime_now = str(datetime.datetime.now())
    time_seconds = time.time()

    status_dict = dict()
    status_dict['gdc_uuid'] = gdc_uuid
    status_dict['datetime_now'] = datetime_now
    status_dict['hostname'] = hostname
    status_dict['host_ipaddress'] = host_ipaddress
    status_dict['host_mac'] = host_mac
    status_dict['num_threads'] = int(num_threads)
    status_dict['repo'] = repo
    status_dict['repo_hash'] = repo_hash
    status_dict['run_uuid'] = [run_uuid]
    status_dict['s3_bam_url'] = s3_bam_url
    status_dict['status'] = status
    status_dict['time_seconds'] = time_seconds

    df = pd.DataFrame(status_dict)
    df.to_sql(table_name, engine, if_exists='append')
    return

if __name__ == '__main__':
    main()
