# -*- coding: utf-8 *-*
import logging
import json
import os
import pwd
import sys

if sys.version_info[0] >= 3:
    from . import config
    from .dynamodb import DynamoHandler
else:
    import config
    from dynamodb import DynamoHandler

logger = logging.getLogger(config.Appl)
logger.setLevel(logging.DEBUG)

handler = DynamoHandler.to(config.Table,
                           config.Region,
                           config.AccessKeyId,
                           config.SecretAccessKey)
logger.addHandler(handler)

def info(str, meta=None):
    if meta:
        d = {'meta': json.dumps({'Appl': config.Appl, 'User': pwd.getpwuid(os.getuid()).pw_name, 'Data': meta})}
    else:
        d = {'meta': json.dumps({'Appl': config.Appl, 'User': pwd.getpwuid(os.getuid()).pw_name})}
    logger.info(str, extra=d)

def debug(str, meta=None):
    if meta:
        d = {'meta': json.dumps({'Appl': config.Appl, 'User': pwd.getpwuid(os.getuid()).pw_name, 'Data': meta})}
    else:
        d = {'meta': json.dumps({'Appl': config.Appl, 'User': pwd.getpwuid(os.getuid()).pw_name})}
    logger.debug(str, extra=d)

def warning(str, meta=None):
    if meta:
        d = {'meta': json.dumps({'Appl': config.Appl, 'User': pwd.getpwuid(os.getuid()).pw_name, 'Data': meta})}
    else:
        d = {'meta': json.dumps({'Appl': config.Appl, 'User': pwd.getpwuid(os.getuid()).pw_name})}
    logger.warning(str, extra=d)

def error(str, meta=None):
    if meta:
        d = {'meta': json.dumps({'Appl': config.Appl, 'User': pwd.getpwuid(os.getuid()).pw_name, 'Data': meta})}
    else:
        d = {'meta': json.dumps({'Appl': config.Appl, 'User': pwd.getpwuid(os.getuid()).pw_name})}
    logger.error(str, extra=d)