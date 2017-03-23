import argparse
import logging
import sys

import assetadapter.common as core
import rpc.server as rpcserver

defaultMessageQueueConfiguration = {
    'mq': {
        'host': 'localhost',
        'port': 5672,
        'username': 'hedgehog',
        'password': 'qwe123',
        'exchange': 'visa_rpc'
    }
}

defaultPyVisaConfiguration = {
    'assetadapter': {
        'inventory': 'local.yml',
        # 'backend': '@py'
        'backend': 'sagax-env.yml@sim'
    }
}


def main():
    # Load RabbitMQ configuration.
    externalizedMessageQueueConfiguration = core.loadConfiguration("mq.yml", defaults=defaultMessageQueueConfiguration)
    # Load Visa configuration
    externalizedVisaConfiguration = core.loadConfiguration("visa.yml", defaults=defaultPyVisaConfiguration)

    # Parse command line arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument("-H", "--host", help="Automation server host of field agent.", type=str, default='localhost')
    parser.add_argument("-V", "--assetadapter", help="PyVISA assetadapter backend.", type=str, default='@py')
    parser.add_argument("-e", "--exchange", help="RabbitMQ exchange for RPC.", type=str, default='')
    parser.add_argument("-u", "--username", help="RabbitMQ username.", type=str, default='guest')
    parser.add_argument("-P", "--port", help="RabbitMQ port.", type=int, default=5672)
    parser.add_argument("-p", "--password", help="RabbitMQ password.", type=str, default='guest')
    parser.add_argument("-v", "--verbose", help="Increase output verbosity.", action="store_true")
    parser.add_argument("-l", "--logfile", help="Logging to file.", type=str, default="~/.hedgehog/log/output.log")
    commandLineArguments = parser.parse_args()

    # Setup logging
    if commandLineArguments.verbose:
        root = core.setupLogging(logfile=commandLineArguments.logfile, logging_level=logging.DEBUG)
    else:
        root = core.setupLogging(logfile=commandLineArguments.logfile, logging_level=logging.INFO)

    # Assemble configuration
    # configuration = {
    #     **externalizedMessageQueueConfiguration,
    #     **externalizedVisaConfiguration
    # }

    # Initialize VISA RPC server
    server = rpcserver.VisaRpcServer(
        host=externalizedMessageQueueConfiguration['mq']['host'],
        username=externalizedMessageQueueConfiguration['mq']['username'],
        password=externalizedMessageQueueConfiguration['mq']['password'],
        visa_library=externalizedVisaConfiguration['assetadapter']['backend'],
        exchange=externalizedMessageQueueConfiguration['mq']['exchange']
    )

    logging.info('VISA RPC SERVER CONFIGURATION BEGIN ===============================')
    logging.info(externalizedMessageQueueConfiguration)
    logging.info(externalizedVisaConfiguration)
    logging.info('VISA RPC SERVER CONFIGURATION END =================================')

    try:
        server.start()
    except KeyboardInterrupt:
        logging.info('Closed by user.')

    server.stop()