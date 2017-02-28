'''
Created on Aug 19, 2016

@author: grastogi
'''
import argparse
import logging
import sys
from requests.packages import urllib3
from avi.sdk.avi_api import ApiSession
from copy import deepcopy

logger = logging.getLogger(__name__)
ch = logging.StreamHandler(sys.stdout)
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
root_logger.addHandler(ch)
urllib3.disable_warnings()


class AnalyticsApiExamples(object):
    """
    """
    def __init__(self, api):
        self.api = api

    def fill_params(self, metrics, step, limit, start, stop, params):
        if step:
            params['step'] = step
        if limit:
            params['limit'] = limit
        if start:
            params['start'] = start
        if stop:
            params['stop'] = stop
        if metrics:
            params['metric_id'] = metrics
        return params

    def collections_api(
            self, entity_uuid, pool_uuid, server, metric_ids, step, limit,
            start, stop):
        path = 'analytics/metrics/collection/?'
        params = self.fill_params(metric_ids, step, limit, start, stop)
        creq = {'metric_requests': []}

        # adding first request
        req = deepcopy(params)
        req['entity_uuid'] = entity_uuid
        if pool_uuid:
            req['pool_uuid'] = pool_uuid
        if server:
            req['server'] = server
        





if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--option',
                        choices=['collections_api'],
                        help='list of example operations',
                        default='collections_api')

    parser.add_argument('-e', '--entity_uuid',
                        help='VirtualService, SE or VM UUID',
                        default='')
    parser.add_argument(
        '-s', '--server_ips',
        help='Pool Server IPs comma separated Eg. 1.1.1.1,2.2.2.2',
        default='1.1.1.1,1.1.1.2')
    parser.add_argument('-u', '--user', help='controller user',
                        default='admin')
    parser.add_argument('-p', '--password', help='controller user password',
                        default='avi123')
    parser.add_argument('-t', '--tenant', help='tenant name',
                        default=None)
    parser.add_argument('--tenant-uuid', help='tenant uuid',
                        default=None)
    parser.add_argument('-c', '--controller_ip', help='controller ip')
    parser.add_argument('-m', '--metric_id',
                        help='Comma separated metric ids',
                        default='l4_client.avg_bandwidth')
    parser.add_argument('-s', '--step',
                        help='step for analytics APIs',
                        default=300)
    parser.add_argument('-l', '--limit',
                        help='Comma separated metric ids',
                        default=5, type=int)
    parser.add_argument('--start',
                        help='ISO format timestamp',
                        default='')
    parser.add_argument('--stop',
                        help='ISO format timestamp',
                        default='')

    args = parser.parse_args()
    print 'parsed args', args
    api = ApiSession.get_session(
            args.controller_ip, args.user, args.password,
            tenant=args.tenant, tenant_uuid=args.tenant_uuid)

    eg = AnalyticsApiExamples(api)

    fn = getattr(eg, args.option)
    fn(args.entity_uuid, args.pool_uuid, args.server, args.metrics,
       args.step, args.limit, args.start, args.stop)
