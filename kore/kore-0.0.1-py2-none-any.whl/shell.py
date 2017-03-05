import logging
import sys

from kore.parsers.appparse import AppParser
from kore import config_factory, container_factory

if __name__ == '__main__':
    sh = logging.StreamHandler()
    logger = logging.getLogger('kore')
    logger.addHandler(sh)
    logger.setLevel(logging.DEBUG)
    # import ipdb; ipdb.set_trace()
    parser = AppParser()
    arguments = parser.parse_args(sys.argv[1:])
    config = config_factory.create(
        arguments.config_type, **dict(arguments.config_opt))
    container = container_factory.create(config=config)
    exit()
