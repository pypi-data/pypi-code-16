import logging
import logging.config


FORMAT = '[%(asctime)s] %(levelname)s pid:%(process)d %(name)s:%(lineno)d %(message)s'
def setup_logging(sentry_dsn=None, level=logging.INFO):
    configuration = {
        'version'   : 1,
        'disable_existing_loggers'  : False,
        'formatters'                : {
            'standard'              : {
                'format'            : FORMAT,
                'dateformat'        : '%d/%b/%Y:%H:%M:%S %z',
            },
        },
        'handlers'                  : {
            'console'               : {
                'level'             : level,
                'class'             : 'logging.StreamHandler',
                'formatter'         : 'standard',
            },
        },
        'loggers'                   : {
            ''                      : {
                'handlers'          : ['console'],
                'level'             : level,
                'propogate'         : True,
            },
        },
    }
    if sentry_dsn:
        configuration['handlers']['sentry'] = {
            'level' : 'ERROR',
            'class' : 'raven.handlers.logging.SentryHandler',
            'dsn'   : sentry_dsn,
        }
        configuration['loggers']['']['handlers'].append('sentry')
    logging.config.dictConfig(configuration)
