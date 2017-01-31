import logging
from pydoc import locate
from functools import reduce
from urllib import parse

import requests
from requests_oauthlib import OAuth1

import asyncio

from osaapi import OSA, Transaction

from apslite_agent.config import get_config
from apslite_agent.utils import check, request
from apslite_agent.tasks import base

logger = logging.getLogger(__name__)


def mgetattr(obj, attr):
    return reduce(getattr, [obj] + attr.split('.'))


class OpenAPI(base.Task):
    name = 'openapi'

    def __init__(self, openapi, rest_url):
        self.openapi = openapi
        self.results = {}
        self.rest_url = rest_url.rstrip('/')

    async def remove_old_oauth(self, url, headers, key, **kwargs):
        url = '{}{}'.format(self.rest_url, url)

        try:
            res = await request(method='GET', url=url, headers=headers, verify=False)
            instances = res.json()
        except Exception as e:
            logger.error("Remove old oauth error: %s", e)
            return {'error': 'remove_old_oauth',
                    'message': 'Remove old oauth error: {}'.format(e)}

        for instance in instances:
            if 'oauth' in instance.get('aps', {}).get('auth', {})\
                    and instance['aps']['auth']['oauth'].get('key', '') == key:
                try:
                    ret = await request(
                        url='{}{}'.format(url, instance['aps']['id']),
                        headers=headers,
                        timeout=20,
                        **kwargs,
                    )
                    if ret.status_code != 204:
                        raise Exception(ret.content)
                except Exception as e:
                    logger.error("Remove old oauth error: %s", e)
                    return {'error': 'remove_old_oauth',
                            'message': 'Remove old oauth error: {}'.format(e)}
        return {}

    async def set_oauth(self, url, headers, **kwargs):
        url = '{}{}'.format(self.rest_url, url)

        try:
            res = await request(method='GET', url=url, headers=headers, verify=False)
            instances = res.json()
            resource_id = self.results['app_instance']['application_resource_id']
        except Exception as e:
            logger.error("Remove old oauth error: %s", e)
            return {'error': 'remove_old_oauth',
                    'message': 'Remove old oauth error: {}'.format(e)}

        for instance in instances:
            if instance.get('app', {}).get('aps', {}).get('id', '') == resource_id:
                try:
                    ret = await request(
                        url='{}{}'.format(url, instance['aps']['id']),
                        headers=headers,
                        timeout=20,
                        **kwargs,
                    )
                    if ret.status_code != 204:
                        raise Exception(ret.content)
                except Exception as e:
                    logger.error("Set oauth error: %s", e)
                    return {'error': 'oauth_error',
                            'message': 'Set oauth error: {}'.format(e)}
        return {}

    async def get_application_id(self, headers):
        url = '{}/aps/2/applications/'.format(self.rest_url)

        try:
            res = await request(method='GET', url=url, headers=headers, verify=False)
            instances = res.json()
            resource_id = self.results['app_instance']['application_resource_id']
        except Exception as e:
            logger.error("Get applications id error: %s", e)
            return None

        for instance in instances:
            if instance.get('app', {}).get('aps', {}).get('id', '') == resource_id:
                return instance['aps']['id']

        logger.error("Get applications id error")
        return None

    async def get_account_uuid(self, app, headers, account_id):
        try:
            account_url = ('{}/aps/2/resources?implementing('
                           'http://parallels.com/aps/types/pa/account/1.2),eq(id,{})')

            res = await request(method='GET', headers=headers,
                                verify=False,
                                url=account_url.format(self.rest_url,
                                                       self.results[account_id]['account_id']))

            account_uuid = res.json()[0]['aps']['id']
        except Exception as e:
            logger.error("Get account UUID error: %s", e)
            return None
        return account_uuid

    async def get_tenant_for_account(self, app, headers, account_uuid):
        try:
            tenant_url = '{}/aps/2/resources/?implementing({}),eq(oaAccount.aps.id,{})'
            tenant_resources = tenant_url.format(self.rest_url,
                                                 app['tenant']['type'],
                                                 account_uuid)
            res = await request(method='GET', url=tenant_resources, headers=headers, verify=False)
            tenant = res.json()[0]
        except Exception as e:
            logger.error("Get tenant error: %s, %s", e, e.__class__)
            return None

        return tenant

    async def get_application(self, application_id, headers):
        if not application_id:
            return application_id

        url = '{}/aps/2/applications/{}'.format(self.rest_url, application_id)

        try:
            res = await request(method='GET', url=url, headers=headers, verify=False)
            instance = res.json()
            return instance
        except Exception as e:
            logger.error("Get applications id error: %s", e)
            return None

    async def assign_users(self, url, headers, account, user_license=None, **kwargs):
        url = '{}{}'.format(self.rest_url, url)
        app = await self.get_application(await self.get_application_id(headers), headers)
        if not app:
            logger.error("Get application error")
            return {'error': 'get_application', 'message': 'Get application error'}

        account_uuid = await self.get_account_uuid(app, headers, account)
        if not account_uuid:
            logger.error("Get account UUID error")
            return {'error': 'get_account_uuid', 'message': 'Get account UUID error'}

        tenant = await self.get_tenant_for_account(app, headers, account_uuid)
        if not tenant:
            logger.error("Get tenant error")
            return {'error': 'get_tenant', 'message': 'Get tenant error'}

        headers.update({'APS-Subscription-ID': tenant['aps']['subscription']})

        try:
            res = await request(method='GET', url=url.format(account_uuid=account_uuid),
                                headers=headers,
                                verify=False)
            users = res.json()
        except Exception as e:
            logger.error("Get account users error: %s", e)
            return {
                'error': 'account_users',
                'message': 'Get account users error: {}'.format(e),
            }

        result = {}
        for (num, user) in enumerate(users):
            user_data = {
                'aps': {
                    'type': app['user']['type'],
                },
                'user': {
                    'aps': {
                        'id': user['aps']['id'],
                    },
                },
            }

            if user_license:
                user_data['resource'] = user_license

            try:
                ret = await request(method='POST',
                                    url='{}/aps/2/resources/'.format(self.rest_url),
                                    headers=headers,
                                    timeout=20,
                                    verify=False,
                                    json=user_data,
                                    )

                if ret.status_code != 200:
                    raise Exception(ret.content)

                data = ret.json()
                result['user{}'.format(num)] = {
                    'app_user_id': data.get('userId', ''),
                    'app_user_aps_id': data['aps']['id'],
                    'oa_user_id': user['userId'],
                    'oa_user_aps_id': user['aps']['id'],
                }

            except Exception as e:
                logger.error("Assign users error: %s", e)
                return {'error': 'assign_users',
                        'message': 'Assign users error: {}'.format(e)}

        return result

    async def set_user_license(self, headers, user_uuid, user_license, **kwargs):
        url = '{}/aps/2/resources/{}'.format(self.rest_url, user_uuid)
        try:
            res = await request('PUT', url, headers=headers, verify=False,
                                json={'resource': user_license})

            if res.status_code not in (200, 400):
                raise Exception(res.content.decode())

            result = res.json()
        except Exception as e:
            logger.error("Change user license error: %s", e)
            return {'error': 'set_user_license',
                    'message': 'Change user license error: {}'.format(e)}
        return result

    async def user_login(self, headers, user_uuid, **kwargs):
        url = '{}/aps/2/resources/{}/login'.format(self.rest_url,
                                                   user_uuid)
        try:
            res = await request(method='GET', url=url, headers=headers, verify=False)
            result = res.text

            if res.status_code != 200:
                raise Exception(result)
        except Exception as e:
            logger.error("Get user login link error: %s", e)
            return {'error': 'user_login',
                    'message': 'Get user login link error: {}'.format(e)}

        return {'link': result}

    async def admin_login(self, headers, account, **kwargs):
        url_template = ('{}/aps/2/resources?implementing('
                        'http://parallels.com/aps/types/pa/admin-user/1.2)')

        url = url_template.format(self.rest_url)
        try:
            res = await request(method='GET', url=url, headers=headers, verify=False)

            if res.status_code != 200:
                raise Exception(res.content.decode())
        except Exception as e:
            logger.error("Get admins error: %s", e)
            return {'error': 'admin_login', 'message': 'Get admins error: {}'.format(e)}

        admin_user_id = res.json()[0]['userId']

        api = OSA(**self.openapi)
        loop = asyncio.get_event_loop()
        res = await loop.run_in_executor(None,
                                         lambda: api.APS.getUserToken(user_id=admin_user_id))
        admin_token = res['result']['aps_token']
        headers.update({'APS-Token': admin_token})

        if res['status'] != 0:
            return {'error': 'admin_login', 'message': 'Failed to get user token'}

        app = await self.get_application(self.get_application_id(headers), headers)
        if not app:
            logger.error("Get application error")
            return {'error': 'get_application', 'message': 'Get application error'}

        account_uuid = await self.get_account_uuid(app, headers, account)
        if not account_uuid:
            logger.error("Get account UUID error")
            return {'error': 'get_account_uuid', 'message': 'Get account UUID error'}

        tenant = await self.get_tenant_for_account(app, headers, account_uuid)
        if not tenant:
            logger.error("Get tenant error")
            return {'error': 'get_tenant', 'message': 'Get tenant error'}

        headers.update({'APS-Subscription-ID': tenant['aps']['subscription']})

        url = '{}/aps/2/resources/{}/adminlogin'.format(
            self.rest_url, tenant['aps']['id'])

        try:
            res = await request(method='GET', url=url, headers=headers, verify=False)
            result = res.text

            if res.status_code != 200:
                raise Exception(result)
        except Exception as e:
            logger.error("Get admin login link error: %s", e)
            return {'error': 'admin_login',
                    'message': 'Get admin login link error: {}'.format(e)}

        return {'link': result}

    async def remove_users(self, headers, **kwargs):
        url_template = '{}/aps/2/resources/{}'
        users = self.results['assign_users']
        for user in users:
            uuid = users[user]['app_user_aps_id']
            url = url_template.format(self.rest_url, uuid)
            try:
                res = await request('DELETE', url, headers=headers, verify=False)

                if res.status_code not in (200, 204):
                    raise Exception(res.status_code)
            except Exception as e:
                logger.error("Remove user error: %s", e)
                return {'error': 'remove_users',
                        'message': 'Remove user error: {}'.format(e)}
        return {}

    async def collect_usage(self, url, headers, **kwargs):
        app_id = await self.get_application_id(headers)

        if not app_id:
            logger.error("Get application error")
            return {'error': 'get_application',
                    'message': 'Get application error'}

        try:
            res = await request(
                method='GET',
                url='{}{}'.format(self.rest_url, url),
                headers=headers,
                verify=False,
                timeout=20,
            )
            periodic_resource_id = res.json()[0]['aps']['id']
        except Exception as e:
            logger.error("Get periodic task error: %s", e)
            return {'error': 'get_periodic_task',
                    'message': 'Get periodic task error: {}'.format(e)}

        path = '/aps/2/resources/{}/tasks'.format(periodic_resource_id)
        query = {'taskType': 'resourceUsage', 'appInstanceId': app_id}
        url = parse.urlunparse(parse.urlparse(self.rest_url)._replace(
            path=path, query=parse.urlencode(query)))
        try:
            res = await request(
                method='PUT',
                url=url,
                headers=headers,
                timeout=20,
                verify=False,
            )
            if res.status_code != 200:
                raise Exception(res.content.decode())
        except Exception as e:
            logger.error("Collect usage error: %s", e)
            return {'error': 'collect_usage',
                    'message': 'Collect usage error: {}'.format(e)}

        return {'url': url}

    async def check_package_instance(self, url, headers, **kwargs):
        url = '{}{}'.format(self.rest_url, url)

        try:
            res = await request(
                method='GET',
                url=url,
                headers=headers,
                timeout=20,
                **kwargs,
            )

            if res.status_code != 200:
                raise Exception(res.content)

            instances = res.json()
            instances_count = len(instances)

            if instances_count > 1:
                raise Exception('HUB have multiple instances')

            if instances_count == 1 and instances[0]['aps']['status'] != 'aps:ready':
                raise Exception('Instance not ready')

        except Exception as e:
            logger.error("Check package instance error: %s", e)
            return {'error': 'check_package_instance',
                    'message': 'Check package instance error: {}'.format(e)}

        return {'count': instances_count}

    async def healthcheck(self, url, key, secret, **kwargs):
        auth = OAuth1(client_key=key, client_secret=secret)
        res = await request(method='GET', url=url, auth=auth)
        if res.status_code == 200:
            return {}
        else:
            return {'error': 'healthcheck',
                    'message': 'Connector returned status code {}'.format(res.status_code)}

    async def url_poll(self, headers, url, retry, wait, success, interval, **kwargs):
        report_field = kwargs.get('report_field')
        while retry > 0:
            retry -= 1
            res = await request(method='GET', url=url, headers=headers, verify=False)
            result = res.json()
            report = result.get(report_field, result) if report_field else result

            wait_status = check(result, wait)
            success_status = check(result, success)

            if wait_status:
                await asyncio.sleep(interval)
            elif success_status:
                return {}
            else:
                return {'error': True, 'message': report}
        error_message = kwargs.get('error_message', 'Error polling URL')
        return {'error': 'url_poll', 'message': error_message}

    async def openapi_poll(self, func, data, retry, interval, wait, success, **kwargs):
        start = 0
        loop = asyncio.get_event_loop()

        while start < retry:
            res = await loop.run_in_executor(None, lambda: func(**data))

            if res['status'] != 0 or 'result' not in res:
                return res

            wait_status = check(res['result'], wait)
            success_status = check(res['result'], success)

            if wait_status:
                start += 1
                await asyncio.sleep(interval)
            elif success_status:
                return res
            else:
                res['error'] = True
                res['message'] = kwargs.get('error_message', 'Error')
                return res

        return {'error': 'openapi_poll', 'message': 'Polling error'}

    async def run(self):
        self.results = self.data['results'] if 'results' in self.data else {}

        if not self.openapi:
            return self.result('Error', "Improperly configured")

        try:
            methods = self.data['methods']
        except IndexError:
            return self.result('Error', "Missing required parameter: 'methods'")

        api = OSA(**self.openapi)

        for method in methods:
            try:
                args = self.get_args(method.get('args', {}))

                logger.info("Calling OpenAPI method '%s' with arguments: %s",
                            method.get('name'),
                            args)

                if 'type' not in method or ('type' in method and method['type'] == 'openapi'):
                    def run():
                        return mgetattr(api, method['name'])(**args)

                    def run_async():
                        if method.get('transaction', True):
                            with Transaction(api) as transaction:
                                args['txn_id'] = transaction.txn_id
                                ret = run()
                        else:
                            ret = run()
                        return ret

                    loop = asyncio.get_event_loop()
                    ret = await loop.run_in_executor(None, run_async)

                elif method['type'] == 'rest':
                    # args.url for substituting parameters
                    args['url'] = '{}{}{}'.format(
                        self.rest_url, method['name'], args.get('url', ''),
                    )
                    ret = requests.request(**args).json()
                    logger.info('REST Api data: %s', ret)
                elif method['type'] == 'workaround' and hasattr(self, method['name']):
                    ret = await getattr(self, method['name'])(**args)
                elif method['type'] == 'openapi.poll':
                    args['func'] = mgetattr(api, method['name'])
                    ret = await self.openapi_poll(**args)
                elif method['type'] == 'url.poll':
                    ret = await self.url_poll(**args)
                elif method['type'] == 'break':
                    ret = {}

                    if args['need_break']:
                        self.results['_'] = ret
                        break

                if 'error' in ret or ('status' in ret and ret['status'] != 0):
                    error_message = ret['message'] if 'message' in ret else 'Error'
                    raise Exception(ret.get('error_message', error_message))

                result = ret.get('result', ret)

                self.results[method.get('id', '')] = result
                self.results['_'] = result
            except Exception as e:
                logger.exception("openapi task error")

                self.data['results'] = self.results
                return self.result('Error', str(e), self.data)

        self.results.pop('_')
        self.data['results'] = self.results

        return self.result('OK', '', self.data)

    def get_args(self, method_args):
        """
        Iterate over existing results and supplied args, substituting @N:param_name
        with actual parameter value from Nth result.
        """

        args = {}

        for arg, value in method_args.items():
            if isinstance(value, list):
                new_value = []
                for item in value:
                    if isinstance(item, dict):
                        item = self.get_args(item)
                    new_value.append(item)
                args[arg] = new_value
            elif isinstance(value, dict):
                args[arg] = self.get_args(value)
            elif isinstance(value, str) and value.startswith('@'):
                try:
                    values = value[1:].split(':')
                    _type = None
                    if len(values) == 2:
                        rid, key = values
                    else:
                        rid, key, _type = values

                    args[arg] = reduce(lambda val, k: val[k],
                                       key.split('.'),
                                       self.results[rid])
                    if _type:
                        args[arg] = locate(_type)(args[arg])

                except Exception:
                    logger.warning("Skipping parameter that looks like a reference, but is badly "
                                   "formatted: '%s'",
                                   value)
                    args[arg] = value
            else:
                args[arg] = value

        return args


def task_factory(**kwargs):
    c = get_config()
    openapi = c.get('oa', {}).get('openapi', {})
    rest_url = c.get('oa', {}).get('rest_url', '')

    return {
        OpenAPI.name: OpenAPI(openapi, rest_url),
    }
