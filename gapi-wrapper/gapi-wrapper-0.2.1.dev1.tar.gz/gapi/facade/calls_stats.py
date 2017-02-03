# -*- coding: utf-8 -*-
import datetime

from gapi.facade.calls import FacadeCalls
from gapi.facade.result_fields import (AdwInteger, AdwDate, AdwANSI, AdwPercent, AdwFloat, AdwMoney, AdwUnicode)
from gapi.utils import to_list

DEFAULT_STATS_DATES_DEPTH = 14


class GetStatsBase(FacadeCalls):
    params = dict(field_groups=None, campaign_ids=None, date_from=None, date_till=None)
    returns = dict()
    service_name = None

    def handle(self):
        filter_ = self._get_filter()
        date_till = self._get_param('date_till')
        if date_till is None:
            date_till = datetime.date.today()
        date_from = self._get_param('date_from')
        if date_from is None:
            date_from = date_till - datetime.timedelta(days=DEFAULT_STATS_DATES_DEPTH)
        result = self.service(self.service_name,
                              params=dict(
                                  fields=self.plain_fields,
                                  date_from=date_from,
                                  date_till=date_till,
                                  filter_=filter_,
                              ))
        return result

    def _get_filter(self):
        filter_ = []
        campaign_ids = self._get_param('campaign_ids')
        if campaign_ids:
            filter_.append('CampaignId IN [{}]'.format(','.join(to_list(campaign_ids))))
        return filter_


class GetCampaignStats(GetStatsBase):
    returns = dict(
        base=(
            AdwInteger('CampaignId'),
            AdwDate('Date'),
            AdwANSI('AccountCurrencyCode'),
            AdwANSI('AdNetworkType1'),
            AdwInteger('Impressions'),
            AdwInteger('Clicks'),
            AdwPercent('Ctr'),
            AdwFloat('AveragePosition'),
            AdwMoney('AverageCpc'),
            AdwMoney('Cost'),
            AdwMoney('Amount'),
            AdwInteger('BudgetId'),
        ),
        bidding=(
            AdwInteger('BiddingStrategyId'),
            AdwANSI('BiddingStrategyType'),
        ),
        lost=(
            AdwANSI('SearchBudgetLostImpressionShare'),
            AdwANSI('ContentBudgetLostImpressionShare'),
            AdwANSI('SearchRankLostImpressionShare'),
            AdwANSI('ContentRankLostImpressionShare'),
        ),
        conversoins=(
            AdwFloat('ConversionValue'),
            # AdwInteger('ConvertedClicks'),
        ),
        share=(
            AdwANSI('SearchExactMatchImpressionShare'),
            AdwANSI('SearchImpressionShare'),
            AdwANSI('ContentImpressionShare'),

        ),
    )
    service_name = 'get_campaign_stats'


class GetSearchQueryStats(GetStatsBase):
    returns = dict(
        base=(
            AdwInteger('KeywordId'),
            AdwInteger('CampaignId'),
            AdwDate('Date'),
            AdwUnicode('Query'),
            AdwUnicode('KeywordTextMatchingQuery'),
            AdwANSI('QueryMatchTypeWithVariant'),
            AdwANSI('AdNetworkType1'),
            AdwInteger('Impressions'),
            AdwInteger('Clicks'),
            AdwANSI('AccountCurrencyCode'),
            AdwMoney('Cost'),
        ),
    )
    service_name = 'get_search_query_stats'


class GetKeywordStats(GetStatsBase):
    params = GetStatsBase.params.copy()
    params.update(include_networks=False)
    returns = dict(
        base=(
            AdwInteger('Id'),
            AdwInteger('AdGroupId'),
            AdwDate('Date'),
            AdwANSI('AccountCurrencyCode'),
            AdwANSI('AdNetworkType1'),
            AdwInteger('Impressions'),
            AdwInteger('Clicks'),
            AdwMoney('Cost'),
        ),
    )
    service_name = 'get_keyword_stats'

    def _get_filter(self):
        filter_ = super(GetKeywordStats, self)._get_filter()
        if not self._get_param('include_networks'):
            filter_.append('AdNetworkType1 IN [SEARCH]')
        return filter_
