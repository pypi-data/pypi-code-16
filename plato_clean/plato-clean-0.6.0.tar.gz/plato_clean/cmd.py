
from gevent import monkey
monkey.patch_all()  # noqa

import functools
import gevent
from gevent.pool import Pool
import sys
import time
import traceback

from sdk.actions import api as sdk_api


from cases.eip import CleanEips
from cases.image import CleanImages
from cases.instance import CleanInstances
from cases.key_pair import CleanKeyPairs
from cases.load_balancer import CleanLoadBalancers
from cases.network import CleanNetworks
from cases.snapshot import CleanSnapshots
from cases.volume import CleanVolumes

from alerts.console import ConsoleAlert
from alerts.slack import SlackAlert
from alerts.sms import SmsAlert

from oslo_config import cfg
COMMON_OPTS = [
    cfg.StrOpt('endpoint', help='api endpoint'),
    cfg.StrOpt('key', help='access key'),
    cfg.StrOpt('secret', help='access secret')
]

CONF = cfg.CONF
CONF.register_cli_opts(COMMON_OPTS)
CONF.register_opts(COMMON_OPTS)

SUPPORTED_SERVICES = ['lcs', 'l2b']


def _get_api(conf):
    if not (conf.key and conf.secret and conf.endpoint):
        raise Exception('You have to specifiy --key, --secret, --endpoint '
                        'in the cli params')

    return sdk_api.setup(access_key=conf.key,
                         access_secret=conf.secret,
                         endpoint=conf.endpoint,
                         is_debug=True)


def _run_case(case, api):
    try:
        case.run(api, gevent.sleep)
    except Exception as ex:
        etype, value, tb = sys.exc_info()
        stack = ''.join(traceback.format_exception(etype,
                                                   value,
                                                   tb,
                                                   100))
        return {
            'message': str(ex),
            'traceback': stack,
            'case': case.__class__.__name__,
        }

    return None


def _alert_exceptions(exceptions):
    if not exceptions:
        return

    alerts = [
        SmsAlert(),
        SlackAlert(),
        ConsoleAlert(),
    ]

    pool = Pool(len(alerts))
    pool.map(lambda x: x.call(exceptions), alerts)
    pool.join()


def clean():
    if len(sys.argv) < 8:
        print('usage: \n\n'
              'plato-clean SERVICE --key KEY --secret SECRET --endpoint ENDPOINT \n'  # noqa
              'SERVICE choose from (lcs, l2b)\n')
        return

    service = sys.argv[1]
    assert service in SUPPORTED_SERVICES, ('unsupported service: %s, '
                                           'only support lcs and l2b')
    start = time.time()
    if service == 'lcs':
        cases = [
            CleanEips(),
            CleanSnapshots(),
            CleanVolumes(),
            CleanInstances(),
            CleanNetworks(),
            CleanImages(),
            CleanKeyPairs(),
        ]
    else:
        cases = [
            CleanLoadBalancers(),
        ]

    CONF(sys.argv[2:])
    API = _get_api(CONF)

    exceptions = map(functools.partial(_run_case, api=API), cases)
    exceptions = filter(lambda x: x, exceptions)
    _alert_exceptions(exceptions)

    end = time.time()
    print ('clean finished in %d seconds' % (end - start))
