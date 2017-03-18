import argparse
import logging


import assetadapter.common as fa_common
import rpc.client as client


def main():
    # Parse command line arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument("-H", "--host", help="Automation server host of field agent.", type=str, default="localhost")
    parser.add_argument("-a", "--alias", help="Alias of the device attended to control.", type=str)
    parser.add_argument("-e", "--exchange", help="RabbitMQ exchange for RPC.", type=str, default='visa_rpc')
    parser.add_argument("-u", "--username", help="RabbitMQ username.", type=str, default='guest')
    parser.add_argument("-p", "--password", help="RabbitMQ password.", type=str, default='guest')
    parser.add_argument("-P", "--port", help="RabbitMQ port.", type=int, default=5672)
    parser.add_argument("-A", "--address", help="Address of the device attended to control.", type=str)
    parser.add_argument("-c", "--command", help="Command transmitted to the device.", type=str, default="?IDN")
    parser.add_argument("-v", "--verbose", help="Increase output verbosity.", action="store_true")
    args = parser.parse_args()

    # Setup logging
    if args.verbose:
        root = fa_common.setupLogging(logging.DEBUG)
    else:
        root = fa_common.setupLogging(logging.INFO)

    root.info('Start Field Agent CLI')
    root.info('Host: ' + args.host)
    root.info('Device: ' + args.alias + ' on ' + args.address)
    root.info('Connect to Field Agent ...')

    rpcClient = client.VisaRpcClient(exchange=args.exchange, host=args.host, port=args.port, username=args.username, password=args.password)
    result = {}
    result[args.alias] = args.address
    rpcClient.alias(result)
    print(args.alias + ':' + args.command + ' -> ' + str(rpcClient.query({
        u'alias': args.alias,
        u'command': args.command
    })))
    rpcClient.dispose()
    root.info('Connection to Field Agent closed.')
