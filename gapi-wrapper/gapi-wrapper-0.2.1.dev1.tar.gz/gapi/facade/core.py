# -*- coding: utf-8 -*-
import logging

from gapi.adwords import AdwordsService
from gapi.exceptions import GAPIException
from gapi.facade.calls import (
    FacadeCalls, GetAccountInfo, GetSubclientsList, GetAdGroups, GetClientsList,
    GetCampaigns, GetKeywords, GetBanners, GetCustomerInfo)
from gapi.facade.mutate import (
    MutateAdsPause, MutateCampaignMinusKeywords, MutateCampaignNegativePlacement, MutateKeywordBidSingle)
from gapi.facade.calls_extensions import (
    GetCampaignExtensions, GetAdGroupExtensions, GetCustomerExtensions)
from gapi.facade.calls_criterions import (
    GetCampaignCriterions, GetAdgroupCriterions, GetSharedCriterions,
    GetCampaignSharedSets)
from gapi.facade.calls_stats import (
    GetCampaignStats, GetSearchQueryStats, GetKeywordStats)

__all__ = ['AdwordsFacadeBase', 'AdwordsFacade']


class AdwordsFacadeBase(object):
    SERVICE_CLASS = AdwordsService
    VERSION = 'v1.0'
    log = logging.getLogger('diglib.gapi.adwords.facade')

    def __init__(self, developer_token, account, client_customer_id=None, cache=None):
        self.service = self.SERVICE_CLASS(
            developer_token=developer_token, account=account,
            client_customer_id=client_customer_id, cache=cache
        )
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if isinstance(attr, type) and issubclass(attr, FacadeCalls):
                adw_call = attr(facade=self)
                setattr(self, attr_name, adw_call)

    def __call__(self, name, *args, **kwargs):
        method = getattr(self, name)
        if isinstance(method, FacadeCalls):
            return method(*args, **kwargs)
        raise GAPIException('No such call {}'.format(name))


class AdwordsFacade(AdwordsFacadeBase):
    get_account_info = GetAccountInfo
    get_subclients_list = GetSubclientsList
    get_clients_list = GetClientsList

    get_campaigns = GetCampaigns
    get_ad_groups = GetAdGroups
    get_banners = GetBanners
    get_keywords = GetKeywords

    get_campaign_stats = GetCampaignStats
    get_campaign_criterions = GetCampaignCriterions
    get_ad_group_criterions = GetAdgroupCriterions
    get_keyword_stats = GetKeywordStats
    get_search_query_stats = GetSearchQueryStats

    get_campaign_extensions = GetCampaignExtensions
    get_ad_group_extensions = GetAdGroupExtensions
    get_customer_extensions = GetCustomerExtensions
    get_customer_info = GetCustomerInfo

    mutate_ads_pause = MutateAdsPause
    mutate_campaign_minus_keywords = MutateCampaignMinusKeywords
    mutate_campaign_negative_placement = MutateCampaignNegativePlacement
    mutate_keyword_bid = MutateKeywordBidSingle

    get_shared_criterions = GetSharedCriterions
    get_campaign_shared_set = GetCampaignSharedSets
