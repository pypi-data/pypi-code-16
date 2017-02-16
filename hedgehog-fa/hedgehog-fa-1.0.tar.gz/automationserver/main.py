import os
import automationserver.server as aut

import logging
import sys
import argparse

import fieldagent.common as fa_common

def main():

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)
    root.info('Start automation server ...')

    parser = argparse.ArgumentParser()
    parser.add_argument("-H", "--host", help="Automation server host of field agent.", type=str, default='localhost')
    parser.add_argument("-V", "--visa", help="PyVISA visa backend.", type=str, default='@py')
    parser.add_argument("-e", "--exchange", help="RabbitMQ exchange for RPC.", type=str, default='')
    parser.add_argument("-u", "--username", help="RabbitMQ username.", type=str, default='guest')
    parser.add_argument("-p", "--password", help="RabbitMQ password.", type=str, default='guest')
    parser.add_argument("-v", "--verbose", help="Increase output verbosity.", action="store_true")
    args = parser.parse_args()

    # Setup logging
    if args.verbose:
        root = fa_common.setupLogging(logging.DEBUG)
    else:
        root = fa_common.setupLogging(logging.INFO)

    server = aut.VisaRpcServer(
        host=args.host,
        username=args.username,
        password=args.password,
        visa_library=args.visa,
        exchange=args.exchange)

    try:
        server.start()
    except KeyboardInterrupt:
        logging.info('Closed by user.')

    server.stop()