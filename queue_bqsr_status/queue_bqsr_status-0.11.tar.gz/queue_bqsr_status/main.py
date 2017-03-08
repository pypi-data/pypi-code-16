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

    parser.add_argument('--bam_signpost_id',
                        required=True
    )
    parser.add_argument('--bam_uuid',
                        required=False
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
    parser.add_argument('--known_snp_signpost_id',
                        required=True
    )
    parser.add_argument('--num_threads',
                        required=True
    )
    parser.add_argument('--reference_fa_signpost_id',
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
    parser.add_argument('--s3_bam_url',
                        required=False
    )
    parser.add_argument('--status',
                        required=True
    )
    parser.add_argument('--table_name',
                        required=True
    )

    args = parser.parse_args()

    bam_signpost_id = args.bam_signpost_id
    hostname = args.hostname
    host_ipaddress = args.host_ipaddress
    host_mac = args.host_mac
    known_snp_signpost_id = args.known_snp_signpost_id
    num_threads = args.num_threads
    reference_fa_signpost_id = args.reference_fa_signpost_id
    repo = args.repo
    repo_hash = args.repo_hash
    run_uuid = args.run_uuid
    status = args.status
    table_name = args.table_name

    if args.bam_uuid is not None:
        bam_uuid = args.bam_uuid
    else:
        bam_uuid = None

    if args.bam_uuid is not None:
        s3_bam_url = args.s3_bam_url
    else:
        s3_bam_url = None

    logger = setup_logging(args, run_uuid)

    sqlite_name = run_uuid + '.db'
    engine_path = 'sqlite:///' + sqlite_name
    engine = sqlalchemy.create_engine(engine_path, isolation_level='SERIALIZABLE')

    datetime_now = str(datetime.datetime.now())
    time_seconds = time.time()

    status_dict = dict()
    status_dict['bam_signpost_id'] = bam_signpost_id
    status_dict['bam_uuid'] = bam_uuid
    status_dict['datetime_now'] = datetime_now
    status_dict['hostname'] = hostname
    status_dict['host_ipaddress'] = host_ipaddress
    status_dict['host_mac'] = host_mac
    status_dict['known_snp_signpost_id'] = known_snp_signpost_id
    status_dict['num_threads'] = int(num_threads)
    status_dict['reference_fa_signpost_id'] = reference_fa_signpost_id
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
