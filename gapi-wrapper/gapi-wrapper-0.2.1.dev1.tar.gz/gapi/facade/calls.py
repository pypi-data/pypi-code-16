# -*- coding: utf-8 -*-
import logging

from gapi.adwords import AdwordsService
from gapi.exceptions import GAPIException
from gapi.facade.result_fields import (
    AdwInteger, AdwUnicode, AdwBoolean, AdwANSI, AdwDate, AdwMoney, AdwFloat, AdwDict, AdwBids,
    AdwUnicodeList)
from gapi.utils import to_list

__all__ = [
    'FacadeCalls', 'GetAccountInfo', 'GetSubclientsList', 'GetClientsList',
    'GetCampaigns', 'GetAdGroups', 'GetBanners', 'GetKeywords',
]


class FacadeCalls(object):
    # TODO по идее это один вызов... зачем множественное число в названи класса?
    params = dict()
    returns = ()  # may be dict(key=(), ...)
    log = logging.getLogger('gapi_wrapper.adwords.facade')

    def __init__(self, facade):
        self.facade = facade
        self.kwargs = None
        self._fields = None
        self.refresh = False

    @property
    def service(self):
        return self.facade.service

    def __call__(self, **kwargs):  # см self.params
        self.kwargs = kwargs
        self.refresh = self.kwargs.get('refresh', False)
        self.service.set_refresh(self.refresh)
        raw_result = self.handle()
        result = self._to_plain(raw_result)
        result = self.finalize_result(result)
        return  result

    def handle(self):
        raise NotImplemented()

    @property
    def plain_fields(self):
        res = []
        for fld in self.fields:
            name = fld.name
            if isinstance(name, list):
                res.extend(name)
            else:
                res.append(name)
        return res

    def _to_plain(self, raw_result):
        result = []
        for row in raw_result:
            result.append(self._obj_to_plain(row))
        return result

    def _obj_to_plain(self, row):
        out_row = dict()
        for field in self.fields:
            if field.fake_field:
                # TODO приводить таки типы к нашим
                continue
            output_name = field.output_name if field.output_name else field.converted_name
            if field.extract(row):
                out_row[output_name] = field.to_plain()
            else:
                out_row[output_name] = None
        return out_row

    def _get_param(self, name):
        return self.kwargs.get(name, self.params[name])

    @property
    def fields(self):
        if self._fields is not None:
            return self._fields
        if isinstance(self.returns, list) or isinstance(self.returns, tuple):
            self._fields = tuple(self.returns)
            return self._fields
        if not isinstance(self.returns, dict):
            raise GAPIException('FacadeCall.returns must be or list or dict! '
                                'While it is {} type'.format(type(self.returns)))
        if 'base' not in self.returns:
            raise GAPIException('FacadeCall.returns dict must contain "base" key!')
        field_groups = self._get_param('field_groups')
        if field_groups == '__all__':
            self._fields = sum((list(x) for x in self.returns.itervalues()), [])
        else:
            self._fields = list(self.returns['base'])
            if field_groups:
                for group in to_list(field_groups):
                    try:
                        extra_fields = self.returns[group]
                    except KeyError:
                        raise GAPIException('No group {} in returns'.format(group))
                    self._fields.extend(extra_fields)
        return self._fields

    def finalize_result(self, result):
        return result


class SingleObjectFacadeCall(FacadeCalls):
    _to_plain = FacadeCalls._obj_to_plain


class GetAccountInfo(SingleObjectFacadeCall):
    returns = (
        AdwInteger('CustomerId'),
        AdwUnicode('CompanyName'),
        AdwBoolean('CanManageClients'),
        AdwANSI('CurrencyCode'),
        AdwANSI('DateTimeZone'),
        AdwBoolean('AutoTaggingEnabled'),
    )

    def handle(self):
        return self.service('get_customer', params=dict(), )


class GetSubclientsList(FacadeCalls):
    returns = (
        AdwInteger('CustomerId'),
        AdwUnicode('Name'),
        # AdwUnicode('CompanyName'),
        #       The companyName field has been removed. This field only contained outdated data and was read-only.
        #       For a descriptive identifier of an account, you can use Customer.descriptiveName.
        #       https://developers.google.com/adwords/api/docs/guides/migration/v201609?hl=ru
        AdwBoolean('CanManageClients'),
        AdwANSI('CurrencyCode'),
        AdwANSI('DateTimeZone'),
    )

    def handle(self):
        return self.service('get_managed_customer', params=dict(fields=self.plain_fields), )


class GetClientsList(FacadeCalls):
    returns = GetSubclientsList.returns

    def handle(self):
        account_service = AdwordsService(
            developer_token=self.service.developer_token, account=self.service.account,
            cache=self.service._cache, refresh=self.refresh
        )
        accoint_info = account_service('get_customer', params=dict())
        service = AdwordsService(
            developer_token=self.service.developer_token, account=self.service.account,
            client_customer_id=accoint_info.customerId,
            cache=self.service._cache, refresh=self.refresh
        )
        return service('get_managed_customer', params=dict(fields=self.plain_fields))


class GetCampaigns(FacadeCalls):
    params = dict(field_groups=None, show_all=False, campaign_ids=None, order_by=None)
    returns = dict(
        base=(
            AdwInteger('Id'),
            AdwUnicode('Name'),
            AdwANSI('Status'),
            AdwANSI('ServingStatus'),
            AdwDate('StartDate'),
            AdwDate('EndDate'),
        ),
        budget=(
            AdwInteger('BudgetId', obtain_name='budget.budgetId'),
            AdwANSI('BudgetStatus', obtain_name='budget.status'),
            AdwMoney('Amount', obtain_name='budget.amount'),
        ),
        network=(
            AdwBoolean('TargetContentNetwork', obtain_name='networkSetting.targetContentNetwork'),
            AdwBoolean('TargetGoogleSearch', obtain_name='networkSetting.targetGoogleSearch'),
            AdwBoolean('TargetPartnerSearchNetwork', obtain_name='networkSetting.targetPartnerSearchNetwork'),
            AdwBoolean('TargetSearchNetwork', obtain_name='networkSetting.targetSearchNetwork'),
        ),
    )

    # {'status': u'PAUSED',
    #  'startDate': u'20150409',
    #  'endDate': u'20371230',
    #  'name': u'Google_Toyota_Alphard_GDN',
    #  'budget': {'status': u'ENABLED',
    #             'amount': {'ComparableValue.Type': u'Money',
    #                        'microAmount': 107730000L},
    #             'budgetId': 398736874L},
    #  'servingStatus': u'SERVING',
    #  'networkSetting': {'targetContentNetwork': True,
    #                     'targetGoogleSearch': False,
    #                     'targetSearchNetwork': False,
    #                     'targetPartnerSearchNetwork': False},
    #  'id': 282770434L}

    def handle(self):
        filter_ = self._get_filter()
        result = self.service('get_campaigns',
                              params=dict(
                                  fields=self.plain_fields, filter_=filter_,
                                  order_by=self._get_param('order_by')
                              ))
        return result

    def _get_filter(self):
        filter_ = []
        show_all = self._get_param('show_all')
        if show_all:
            filter_.append("Status IN [ENABLED, PAUSED, REMOVED]")
        else:
            filter_.append("Status IN [ENABLED, PAUSED]")
        campaign_ids = self._get_param('campaign_ids')
        if campaign_ids:
            filter_.append('CampaignId IN [{}]'.format(','.join(to_list(campaign_ids))))
        return filter_


class GetAdGroups(FacadeCalls):
    params = dict(field_groups=None, show_all=False, campaign_ids=None, order_by=None)
    returns = dict(
        base=(
            AdwInteger('Id'),
            AdwUnicode('Name'),
            AdwANSI('Status'),
        ),
        campaign=(
            AdwInteger('CampaignId'),
            AdwUnicode('CampaignName'),
        ),
        bidding=(
            AdwANSI('ContentBidCriterionTypeGroup'),
            AdwBids(['CpcBid', 'CpmBid'], obtain_name='biddingStrategyConfiguration.bids', output_name='bids'),
            AdwBoolean('EnhancedCpcEnabled',
                       obtain_name='biddingStrategyConfiguration.biddingScheme.enhancedCpcEnabled'),
        )
    )


    # {'status': u'PAUSED',
    #  'campaignName': u'Google_Toyota_Remarketing',
    #  'id': 17661676234L,
    #  'name': u'Common',
    #  'campaignId': 282772474L}

    def handle(self):
        filter_ = self._get_filter()
        result = self.service('get_ad_groups',
                              params=dict(
                                  fields=self.plain_fields, filter_=filter_,
                                  order_by=self._get_param('order_by')
                              ))
        return result

    def _get_filter(self):
        filter_ = []
        show_all = self._get_param('show_all')
        if show_all:
            filter_.append("Status IN [ENABLED, PAUSED, REMOVED]")
        else:
            filter_.append("Status IN [ENABLED, PAUSED]")
        campaign_ids = self._get_param('campaign_ids')
        if campaign_ids:
            filter_.append('CampaignId IN [{}]'.format(','.join(to_list(campaign_ids))))
        return filter_


class GetBanners(FacadeCalls):
    params = dict(field_groups=None, show_all=False, adgroup_ids=None, order_by=None)
    returns = dict(
        base=(
            AdwInteger('Id', obtain_name='ad.id'),
            AdwInteger('AdGroupId'),
            AdwANSI('Status'),
            # AdwBoolean('TrademarkDisapproved'),
        ),
        urls=(
            AdwUnicode('DisplayUrl', obtain_name='ad.displayUrl'),
            AdwUnicodeList('CreativeFinalUrls', obtain_name='ad.finalUrls'),
        ),
        descriptions=(
            AdwUnicode('Description1', obtain_name='ad.description1'),
            AdwUnicode('Description2', obtain_name='ad.description2'),
            AdwUnicode('Headline', obtain_name='ad.headline'),
        )
        # AdwANSI('ApprovalStatus'),
    )

    # https://developers.google.com/adwords/api/docs/reference/v201603/AdGroupAdService.TextAd?hl=ru#field
    # {'status': u'PAUSED',
    #  'approvalStatus': u'FAMILY_SAFE',
    #  'adGroupId': 17661676234L,
    #  'ad': {
    #     'headline': u'Увеличенная выгода на Тойота',
    #     'displayUrl': u'toyota-vnukovo.ru',
    #      'finalUrls': [
    #          u'http://toyota-vnukovo.ru/about/news/avtomobil-biznes-klassa-s-kolossalnoy-vygodoy.tmex?utm_source=google&utm_medium=cpc&utm_term={keyword}&placement={placement}&utm_campaign=Google_Toyota_Common_RM&utm_content=Uvelicennaja-vygoda-na-Toyota'
    #      ],
    #     'description2': u'выгода до 100000р. + льготный кредит',
    #     'description1': u'До 23/11 Недели Осенних Предложений:',
    #     'Ad.Type': u'TextAd',
    #      'type': u'TEXT_AD',
    #      'id': 56277744514L},
    #  'trademarkDisapproved': False}

    def handle(self):
        result = self.service('get_banners',
                              params=dict(
                                  fields=self.plain_fields,
                                  filter_=self._get_filter(),
                                  order_by=self._get_param('order_by')
                              ))
        return result

    def _get_filter(self):
        filter_ = []
        show_all = self._get_param('show_all')
        if show_all:
            filter_.append("Status IN [ENABLED, PAUSED, REMOVED]")
        else:
            filter_.append("Status IN [ENABLED, PAUSED]")
        adgroups_ids = self._get_param('adgroup_ids')
        if adgroups_ids:
            filter_.append('AdGroupId IN [{}]'.format(','.join(to_list(adgroups_ids))))
        return filter_


class GetKeywords(FacadeCalls):
    params = dict(field_groups=None, adgroup_ids=None, order_by=None, show_all=False)
    returns = dict(
        base=(
            AdwInteger('Id', obtain_name='criterion.id'),
            AdwANSI('AdGroupId'),
            AdwANSI('CriterionUse'),
            AdwUnicode('KeywordText', obtain_name='criterion.text'),
            AdwANSI('KeywordMatchType', obtain_name='criterion.matchType'),
            AdwANSI('ApprovalStatus'),
            AdwANSI('DestinationUrl'),
            AdwMoney('FirstPageCpc', obtain_name='firstPageCpc.amount'),
            AdwMoney('TopOfPageCpc', obtain_name='topOfPageCpc.amount'),
            AdwInteger('QualityScore', obtain_name='qualityInfo.qualityScore'),
            AdwANSI('PlacementUrl', obtain_name='criterion.url'),
            AdwANSI('Status', obtain_name='userStatus'),
            AdwANSI('SystemServingStatus'),
        ),
        bidding=(
            AdwFloat('BidModifier'),
            AdwANSI('BiddingStrategyType', obtain_name='biddingStrategyConfiguration.biddingStrategySource'),
            AdwANSI('BiddingStrategySource', obtain_name='biddingStrategyConfiguration.biddingStrategyType'),
            AdwANSI('BidType', obtain_name='biddingStrategyConfiguration.biddingScheme.bidType'),
            AdwBids(['CpcBid', 'CpmBid'], obtain_name='biddingStrategyConfiguration.bids', output_name='bids'),
            AdwBoolean('EnhancedCpcEnabled',
                       obtain_name='biddingStrategyConfiguration.biddingScheme.enhancedCpcEnabled'),
        )
    )

    # https://developers.google.com/adwords/api/docs/reference/v201603/AdGroupCriterionService
    # {'AdGroupCriterion.Type': u'NegativeAdGroupCriterion',
    #  'adGroupId': 23903577758L,
    #  'criterion': {'text': u'lexus',
    #                'matchType': u'BROAD',
    #                'type': u'KEYWORD',
    #                'id': 10092140L,
    #                'Operand.Type': u'Keyword'},
    #  'criterionUse': u'NEGATIVE'}

    def handle(self):
        result = self.service(
            'get_keywords',
            params=dict(
                fields=self.plain_fields,
                filter_=self._get_filter(),
                order_by=self._get_param('order_by'),
            ),
        )
        return result

    def _get_filter(self):
        filter_ = []
        show_all = self._get_param('show_all')
        if show_all:
            filter_.append("Status IN [ENABLED, PAUSED, REMOVED]")
        else:
            filter_.append("Status IN [ENABLED, PAUSED]")
        adgroup_ids = self._get_param('adgroup_ids')
        if adgroup_ids:
            filter_.append('AdGroupId IN [{}]'.format(','.join(to_list(adgroup_ids))))
        return filter_


class GetCustomerInfo(FacadeCalls):
    params = dict(field_groups=None)
    returns = dict(
        base=(
            AdwInteger('CustomerId'),
            AdwANSI('CurrencyCode'),
            AdwANSI('DateTimeZone'),
            AdwBoolean('AutoTaggingEnabled'),
            AdwBoolean('TestAccount'),
            AdwBoolean('CanManageClients'),
        ),
        settings=(
            AdwDict('ConversionTrackingSettings'),
            AdwDict('RemarketingSettings'),
            AdwANSI('TrackingUrlTemplate'),
        )
    )

    def handle(self):
        result = self.service('get_customer_info')
        return result


