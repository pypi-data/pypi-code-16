# -*- coding: utf-8 -*-
import csv
import logging
import time
from tempfile import TemporaryFile

import suds

from .core import GoogleService, customer_callable
from .exceptions import (
    APINetworkError, APIQuotaLimit, APIParallelRequests, APIException,
    APIInvalidCredentials, APIValueError, APINotAllowed, APIInternalError)
from .utils import Bunch, to_list, to_google_camel_case, suds_to_dict
from googleads import oauth2, adwords
from googleads.errors import AdWordsReportError, GoogleAdsError

__all__ = ['AdwordsService']


class AdwordsService(GoogleService):
    VERSION = 'v201609'
    PAGE_SIZE = 100
    RETRY_SLEEP_SECS = 1

    NETWORK_RETRIES = 5
    NETWORK_RETRY_SLEEP_TIME = 5
    MAX_CONTINUED_NETWORK_ERRORS = 10
    PARALLEL_REQUEST_RETRIES = 3
    PARALLEL_REQUEST_MAX_RETRY_SLEEP_TIME = 60 * 5
    MAX_CONTINUED_PARALLEL_REQUEST_ERRORS = 3

    log = logging.getLogger('.adwords')

    def __init__(self, developer_token, account, client_customer_id=None, cache=None, refresh=False):
        super(AdwordsService, self).__init__(refresh=refresh)
        self.developer_token = developer_token
        self.account = account
        self.client_customer_id = client_customer_id
        self._cache = cache

        # Теперь клиент ленивый
        self._oauth2_client = None
        self._client = None
        self._services = {}

        self.fields = None
        self.filter = None
        self.order_by = None

    def _get_cache_key(self, name, params):
        return [self.account, self.client_customer_id, name, params]

    def _data_post_processing(self, data):
        data = suds_to_dict(data)
        return data

    def _get_oauth2_client(self, refresh=False):
        if self._oauth2_client is None or refresh:
            self._oauth2_client = oauth2.GoogleRefreshTokenClient(
                client_id=self.account['client_id'],
                client_secret=self.account['client_secret'],
                refresh_token=self.account['refresh_token'],
            )
        return self._oauth2_client

    @property
    def oauth2_client(self):
        return self._get_oauth2_client()

    @oauth2_client.setter
    def oauth2_client(self, value):
        self._oauth2_client = value

    def _get_client(self, refresh=False):
        if self._client is None or refresh:
            self._client = adwords.AdWordsClient(
                developer_token=self.developer_token,
                oauth2_client=self.oauth2_client,
                user_agent=self.USER_AGENT,
                client_customer_id=self.client_customer_id,
            )
        return self._client

    @property
    def client(self):
        return self._get_client()

    @client.setter
    def client(self, value):
        self._client = value

    def _get_service(self, service_name):
        if service_name not in self._services:
            self._services[service_name] = self.client.GetService(service_name, version=self.VERSION)
        return self._services[service_name]

    @customer_callable
    def get_customer(self, ):
        service = self._get_service('CustomerService')
        data = self._exception_wrapper(service.getCustomers)
        return data[0]  # googleads-python-lib/examples/adwords/v201609/extensions/add_site_links.py:44

    @customer_callable
    def get_managed_customer(self, fields):
        selector = dict(fields=fields)
        return self._get_service_data('ManagedCustomerService', selector)

    @customer_callable
    def get_campaigns(self, fields, filter_=None, order_by=None):
        return self._get_by_awql('CampaignService', fields=fields, filter_=filter_, order_by=order_by)

    @customer_callable
    def get_ad_groups(self, fields, filter_=None, order_by=None):
        return self._get_by_awql('AdGroupService', fields=fields, filter_=filter_, order_by=order_by)

    @customer_callable
    def get_banners(self, fields, filter_=None, order_by=None):
        self.filter = to_list(filter_)
        self.filter.append(' AdType IN [TEXT_AD]')
        return self._get_by_awql('AdGroupAdService', fields=fields, filter_=None, order_by=order_by)

    @customer_callable
    def get_keywords(self, fields, filter_=None, order_by=None):
        self.filter = to_list(filter_)
        self.filter.append(' CriteriaType IN [KEYWORD]')
        return self._get_by_awql('AdGroupCriterionService', fields=fields, filter_=None, order_by=order_by)

    @customer_callable
    def get_campaign_stats(self, fields, date_from, date_till, filter_=None):
        return self._get_perf_report(report_name='CAMPAIGN_PERFORMANCE_REPORT',
                                     fields=fields, date_from=date_from, date_till=date_till,
                                     filter_=filter_)

    @customer_callable
    def get_keyword_stats(self, fields, date_from, date_till, filter_=None):
        return self._get_perf_report(report_name='KEYWORDS_PERFORMANCE_REPORT',
                                     fields=fields, date_from=date_from, date_till=date_till,
                                     filter_=filter_)

    @customer_callable
    def get_search_query_stats(self, fields, date_from, date_till, filter_=None):
        return self._get_perf_report(report_name='SEARCH_QUERY_PERFORMANCE_REPORT',
                                     fields=fields, date_from=date_from, date_till=date_till,
                                     filter_=filter_)

    @customer_callable
    def get_campaign_criterion(self, fields, filter_=None):
        return self._get_by_awql('CampaignCriterionService', fields=fields, filter_=filter_)

    @customer_callable
    def get_ad_group_criterion(self, fields, filter_=None):
        return self._get_by_awql('AdGroupCriterionService', fields=fields, filter_=filter_)

    @customer_callable
    def get_campaign_extensions(self, fields, filter_=None):
        return self._get_by_awql('CampaignExtensionSettingService', fields=fields, filter_=filter_)

    @customer_callable
    def get_ad_group_extensions(self, fields, filter_=None):
        return self._get_by_awql('AdGroupExtensionSettingService', fields=fields, filter_=filter_)

    @customer_callable
    def get_customer_extensions(self, fields, filter_=None):
        return self._get_by_awql('CustomerExtensionSettingService', fields=fields, filter_=filter_)

    @customer_callable
    def get_customer_info(self):
        return self._get_service_data_no_paging('CustomerService', method_name='getCustomers')

    @customer_callable
    def get_shared_criterion(self, fields, filter_=None):
        return self._get_by_awql('SharedCriterionService', fields=fields, filter_=filter_)

    @customer_callable
    def get_shared_set(self, fields, filter_=None):
        return self._get_by_awql('SharedSetService', fields=fields, filter_=filter_)

    @customer_callable
    def get_campaign_shared_set(self, fields, filter_=None):
        return self._get_by_awql('CampaignSharedSetService', fields=fields, filter_=filter_)

    def _get_by_awql(self, service, fields, filter_=None, order_by=None):
        self.fields = to_list(fields)
        if filter_ is not None:
            self.filter = to_list(filter_)
        self.order_by = to_list(order_by) if order_by is not None else None
        return self._awql_request(service)

    def _get_perf_report(self, report_name, fields, date_from, date_till, filter_=None):
        self.fields = to_list(fields)
        self.filter = to_list(filter_)
        self.order_by = None
        query = self._get_awql_query(report_name=report_name)
        query += ' DURING {date_from},{date_till}'.format(
            date_from=date_from.strftime('%Y%m%d'),
            date_till=date_till.strftime('%Y%m%d'),
        )
        return self._get_report_awql(query=query)

    def _get_service_data(self, service_name, selector=None):
        service = self._get_service(service_name)
        selector['paging'] = {
            'numberResults': str(self.PAGE_SIZE)
        }
        more_pages = True
        offset = 0
        while more_pages:
            selector['paging']['startIndex'] = str(offset)
            page = self._exception_wrapper(service.get, selector)
            if 'entries' in page:
                for row in page['entries']:
                    yield self._get_bunch(row)
            else:
                break
            offset += self.PAGE_SIZE
            more_pages = offset < int(page['totalNumEntries'])

    def _get_bunch(self, row):
        return Bunch(**{k: v for k, v in row.__dict__.iteritems() if not k.startswith('__')})

    def _get_service_data_no_paging(self, service_name, method_name='get'):
        service = self._get_service(service_name)
        method = getattr(service, method_name)
        data = self._exception_wrapper(method)
        res = [self._get_bunch(row) for row in data]
        return res

    def _awql_request(self, service_name):
        query = self._get_awql_query()
        result = self._get_awql_data(query, service_name)
        return result

    def _get_awql_query(self, report_name=None):
        query = 'SELECT {}'.format(','.join(self.fields))
        if report_name:
            query += ' FROM  {}'.format(report_name)
        if self.filter:
            query += ' WHERE {}'.format(' AND '.join(self.filter))
        if self.order_by:
            query += ' ORDER BY {}'.format(','.join(self.order_by))
        return query

    def _get_awql_data(self, query, service_name):
        service = self._get_service(service_name)
        offset, more_pages = 0, True
        while more_pages:
            page = self._exception_wrapper(service.query, query + ' LIMIT %s, %s' % (offset, self.PAGE_SIZE))
            if 'entries' in page:
                for row in page['entries']:
                    yield self._get_bunch(row)
            else:
                break
            offset += self.PAGE_SIZE
            more_pages = offset < int(page['totalNumEntries'])

    def _exception_wrapper(self, func, *args, **kwargs):
            network_errors, self.parallel_request_errors = 0, 0
            func_signature = '{}({}, {})'.format(func.__name__, args, kwargs)
            while True:
                try:
                    return func(*args, **kwargs)
                except suds.WebFault as exc:
                    try:
                        self._parse_web_fault(exc, func_signature)
                    except APIException:
                        #  пропускаем сформированные _parse_web_fault ошибки
                        raise
                    except Exception as exc:
                        self.log.exception("Can't parse WebFault on {}".format(func_signature))
                        raise APIException('WebFault parse error', exc=exc)
                except Exception as exc:
                    # всё остальное от googleads-python-lib считаем сетевой проблемой
                    network_errors += 1
                    if network_errors > self.NETWORK_RETRIES:
                        self.log.warning('APINetworkError at {}'.format(func_signature))
                        raise APINetworkError('Error on {}'.format(func_signature), exc=exc)
                    time.sleep(self.NETWORK_RETRY_SLEEP_TIME)

    def _parse_web_fault(self, exc, func_signature):
        # suds.WebFault => .../site-packages/suds/__init__.py:71
        # suds.client.SoapClient#process_reply => .../site-packages/suds/client.py:669
        if not hasattr(exc.fault, 'detail'):
            raise APIValueError(message=exc.fault.faultstring)
        error = exc.fault.detail.ApiExceptionFault.errors
        error_type = error.get('ApiError.Type')
        reason = error.get('reason', 'N/A')
        error_string = 'reason {reason}, fieldPath {fieldPath}, trigger {trigger}'.format(
            reason=reason,
            fieldPath=error.get('fieldPath', 'N/A'),
            trigger=error.get('trigger', 'N/A'),
        )
        if error_type == 'RateExceededError':
            sleep_time = int(error['retryAfterSeconds'])
            if sleep_time > self.PARALLEL_REQUEST_MAX_RETRY_SLEEP_TIME:
                self.log.warning('APIQuotaLimit at {}, sleep time {}'.format(func_signature, sleep_time))
                raise APIQuotaLimit('Adwords RateExceededError sleep time {}'.format(sleep_time))
            self.parallel_request_errors += 1
            if self.parallel_request_errors > self.PARALLEL_REQUEST_RETRIES:
                self.log.warning('Adwords RateExceededError at {}'.format(func_signature))
                raise APIParallelRequests('{}:{}:{}'.format(
                    str(error['rateScope']),
                    str(error['rateName']),
                    func_signature))
            time.sleep(sleep_time)  # если из _parse_web_fault ничего не рейзится - переповтор
        elif error_type in ('QuotaCheckError', 'EntityCountLimitExceeded'):
            self.log.warning('{} at {}: error_string'.format(error_type, func_signature, error_string))
            raise APIQuotaLimit(error_string)
        elif error_type == 'SizeLimitError':
            if reason == 'INTERNAL_STORAGE_ERROR':
                raise APINotAllowed(error_type, error=error_string)
            raise APIValueError(error_type, error=error_string)
            # APIValueError == CollectionSizeError CriterionError
        elif error_type in (
                'AuthenticationError',
                'AuthorizationError',
                'EntityAccessDenied',
                'ClientTermsError',
                'OperationAccessDenied',
        ):
            raise APINotAllowed(error_type, error=error_string)
        elif error_type in (
                'InternalApiError',
                'DatabaseError',
        ):
            raise APIInternalError(error_type, error=error_string)
        elif error_type in (
                'AdGroupCriterionError',
                'AdxError',
                'BiddingErrors',
                'CollectionSizeError',
                'CriterionError',
                'DateError',
                'DistinctError',
                'EntityNotFound',
                'ForwardCompatibilityError',
                'IdError',
                'MultiplierError',
                'NewEntityCreationError',
                'NotEmptyError',
                'NullError',
                'OperatorError',
                'PagingError',
                'PolicyViolationError',
                'QueryError',
                'RangeError',
                'RejectedError',
                'RequestError',
                'ReadOnlyError',
                'RequiredError',
                'SelectorError',
                'StatsQueryError',
                'StringFormatError',
                'StringLengthError',
                'UrlError',
        ):
            raise APIValueError(error_type, error=error_string)
        else:
            self.log.warning('WebFault {} at {}'.format(error, func_signature, ))
            raise APIException('WebFault', error=error_string)

    def _get_report_awql(self, query):
        report_downloader = self.client.GetReportDownloader(version=self.VERSION)
        data = []
        with TemporaryFile() as ff:
            #  можно посмотреть на DownloadReportAsStringWithAwql - может будет побыстрее
            try:
                report_downloader.DownloadReportWithAwql(
                    query, 'CSV', ff, skip_report_header=True,
                    skip_column_header=True, skip_report_summary=True)
            except AdWordsReportError as exc:
                # TODO тут по идее будут ошибки сервиса, типа RateExceededError etc, но какой у них формат????
                raise APIException('AdWordsReportError', code=exc.code, content=exc.content, urllib_error=exc.error)
            except GoogleAdsError as exc:
                raise APIException('GoogleAdsError', exc=exc)
            ff.seek(0)
            reader = csv.reader(ff, delimiter=',', quotechar='"')
            fields = [to_google_camel_case(fld) for fld in self.fields]
            for row in reader:
                # example of first two rows (first aka "header", second aka "fields headers")
                # ['CAMPAIGN_PERFORMANCE_REPORT']
                # ['Campaign ID', 'Campaign', 'Campaign state', 'Currency', 'Network', 'Impressions', 'Clicks',
                #  'CTR', 'Avg.position', 'Avg.CPC', 'Cost']
                data.append(dict(zip(fields, row)))
        return data

    def mutate_single(self, service_name, operation):
        try:
            return self._mutate_service_single(service_name, [operation, ])
        except Exception:
            self.log.exception("Mutate service_name={}, operation={})".format(
                service_name, operation))
            raise

    def mutate(self, service_name, operations):
        try:
            return self._mutate_service(service_name, operations=operations)
        except Exception:
            self.log.exception("Mutate service_name={}, operations={})".format(
                service_name, operations[:100]))
            raise

    def _mutate_service_single(self, service_name, operation):
        service = self._get_service(service_name)
        continued_network_errors, continued_parallel_request_errors = 0, 0
        while True:
            try:
                mutate_answer = self._exception_wrapper(service.mutate, operation)
                return mutate_answer.value[0]
            except APINetworkError as exc:
                continued_network_errors += 1
                if continued_network_errors > self.MAX_CONTINUED_NETWORK_ERRORS:
                    raise exc
            except APIParallelRequests as exc:
                continued_parallel_request_errors += 1
                if continued_parallel_request_errors > self.MAX_CONTINUED_PARALLEL_REQUEST_ERRORS:
                    raise exc

    def _mutate_service(self, service_name, operations):
        operations_result = []
        while operations:
            operation = operations.pop(0)
            try:
                res = self._mutate_service_single(service_name, operation)
                res['error'] = None
                operations_result.append(res)
            except APIException as exc:
                res = dict(error=dict(
                    type=exc.__class__.__name__,
                    message=exc.message,
                    data=str(exc.data),
                ))
                operations_result.append(res)
                if isinstance(exc, (APIInvalidCredentials, APINetworkError, APIParallelRequests)):
                    # дальше нельзя - добивам остаток результатов текущей ошибкой и выходим
                    operations_result.extend([res for _ in operations])
                    break
        return operations_result

