# -*- coding: utf-8 -*-
from .calls import FacadeCalls
from .result_fields import (AdwField, AdwInteger, AdwANSI, AdwBoolean, AdwUnicode)
from gapi.utils import to_list


class AdwCriterionDict(AdwField):

    def to_plain(self):
        if "Criterion.Type" in self.value:
            del self.value["Criterion.Type"]
        return dict(self.value)


class GetCriterionsBase(FacadeCalls):
    params = dict(field_groups=None, campaign_ids=None, filter=None)
    # https://developers.google.com/adwords/api/docs/appendix/selectorfields?hl=ru#v201605-CampaignCriterionService
    returns = (
        AdwInteger('CampaignId'),
        AdwANSI('CriteriaType', obtain_name='criterion.type'),
        AdwCriterionDict('Id', obtain_name='criterion', output_name='criterion'),
    )
    service_name = None
    extra_filter = None

    def handle(self):
        filter_ = self._get_filter()
        result = self.service(self.service_name,
                              params=dict(
                                  fields=self.plain_fields,
                                  filter_=filter_,
                              ))
        return result

    def _get_filter(self):
        filter_ = []
        extra_filter = self._get_param('filter')
        if extra_filter:
            filter_.extend(to_list(extra_filter))
        campaign_ids = self._get_param('campaign_ids')
        if campaign_ids:
            filter_.append('CampaignId IN [{}]'.format(','.join(to_list(campaign_ids))))
        if self.extra_filter:
            filter_.extend(to_list(self.extra_filter))
        return filter_


class GetCampaignCriterions(GetCriterionsBase):
    # https://developers.google.com/adwords/api/docs/reference/v201603/CampaignCriterionService.CampaignCriterion?hl=ru#field
    returns = GetCriterionsBase.returns + (
        AdwBoolean('IsNegative'),
        AdwANSI('PlacementUrl', fake_field=True),  # нужно что бы в criterion оно попало
        AdwANSI('UserListId', fake_field=True),  # нужно что бы в criterion оно попало
        AdwBoolean('UserListEligibleForSearch', fake_field=True),
        AdwBoolean('UserListEligibleForDisplay', fake_field=True),
    )
    service_name = 'get_campaign_criterion'


class GetAdgroupCriterions(GetCriterionsBase):
    # https://developers.google.com/adwords/api/docs/reference/v201603/CampaignCriterionService.CampaignCriterion?hl=ru#field
    returns = GetCriterionsBase.returns + (
        AdwInteger('BaseCampaignId'),
        AdwInteger('AdGroupId'),
        AdwANSI('CriterionUse'),
        # TODO приводить таки типы к нашим - сделать контейнер этих полей
        AdwANSI('PlacementUrl', fake_field=True),  # нужно что бы в criterion попало
        AdwANSI('UserListId', fake_field=True),  # нужно что бы в criterion попало
        AdwBoolean('UserListEligibleForSearch', fake_field=True),
        AdwBoolean('UserListEligibleForDisplay', fake_field=True),
        AdwUnicode('KeywordText', fake_field=True),
        AdwANSI('KeywordMatchType', fake_field=True),
    )
    service_name = 'get_ad_group_criterion'


class GetSharedCriterions(GetCriterionsBase):
    params = dict(field_groups=None, shared_set_ids=None, filter=None)
    # https://developers.google.com/adwords/api/docs/appendix/selectorfields?hl=ru#v201609-SharedCriterionService
    # AppId 	MobileApplication.appId 	Yes 	    entries.criterion.appId
    # ChannelId 	YouTubeChannel.channelId 	No 	    entries.criterion.channelId
    # ChannelName 	YouTubeChannel.channelName 	No 	    entries.criterion.channelName
    # CriteriaType 	Criterion.type 	Yes 	    entries.criterion.type
    # DisplayName 	MobileApplication.displayName 	Yes 	    entries.criterion.displayName
    # Id 	Criterion.id 	Yes 	    entries.criterion.id
    # KeywordMatchType 	Keyword.matchType 	Yes 	    entries.criterion.matchType
    # KeywordText 	Keyword.text 	Yes 	    entries.criterion.text
    # Negative 	SharedCriterion.negative 	Yes 	    entries.negative
    # PlacementUrl 	Placement.url 	Yes 	    entries.criterion.url
    # SharedSetId 	SharedCriterion.sharedSetId 	Yes 	    entries.sharedSetId
    # VideoId 	YouTubeVideo.videoId 	No 	    entries.criterion.videoId
    # VideoName 	YouTubeVideo.videoName 	No 	    entries.criterion.videoName
    returns = (
        AdwInteger('Id', obtain_name='criterion.id'),
        AdwInteger('SharedSetId'),
        AdwANSI('CriteriaType', obtain_name='criterion.type'),
        AdwBoolean('Negative'),
        AdwUnicode('KeywordText', obtain_name='criterion.text'),
        AdwUnicode('KeywordMatchType', obtain_name='criterion.matchType'),
        AdwANSI('PlacementUrl', obtain_name='criterion.url'),
    )

    def handle(self):
        filter_ = []
        shared_set_ids = self._get_param('shared_set_ids')
        if shared_set_ids:
            shared_set_ids = map(str, shared_set_ids)
            filter_.append('SharedSetId IN [{}]'.format(','.join(shared_set_ids)))
        extra_filter = self._get_param('filter')
        if extra_filter:
            filter_.extend(to_list(extra_filter))
        result = self.service('get_shared_criterion',
                              params=dict(
                                  fields=self.plain_fields,
                                  filter_=filter_,
                              ))
        return result


class GetCampaignSharedSets(GetCriterionsBase):
    # https://developers.google.com/adwords/api/docs/appendix/selectorfields?hl=ru#v201609-CampaignSharedSetService
    # CampaignId 	CampaignSharedSet.campaignId 	Yes 	entries.campaignId
    # CampaignName 	CampaignSharedSet.campaignName 	No 	entries.campaignName
    # SharedSetId 	CampaignSharedSet.sharedSetId 	Yes 	entries.sharedSetId
    # SharedSetName 	CampaignSharedSet.sharedSetName 	No 	entries.sharedSetName
    # SharedSetType 	CampaignSharedSet.sharedSetType 	Yes 	entries.sharedSetType
    # Status 	CampaignSharedSet.status 	Yes 	entries.status (ENABLED REMOVED UNKNOWN)
    returns = (
        AdwInteger('CampaignId'),
        AdwInteger('SharedSetId'),
    )
    service_name = 'get_campaign_shared_set'
    extra_filter = 'Status IN [ENABLED]'


# class GetSharedSets(GetCriterionsBase):
# TODO пока не нужен, но вдруг... удалить после 01.01.17
#     # https://developers.google.com/adwords/api/docs/appendix/selectorfields?hl=ru#v201609-CampaignSharedSetService
#     # MemberCount 	SharedSet.memberCount 	No 	entries.memberCount
#     # Name 	SharedSet.name 	Yes 	entries.name
#     # ReferenceCount 	SharedSet.referenceCount 	No 	entries.referenceCount
#     # SharedSetId 	SharedSet.sharedSetId 	Yes 	entries.sharedSetId
#     # Status 	SharedSet.status 	Yes 	entries.status (ENABLED REMOVED UNKNOWN)
#     # Type 	SharedSet.type 	Yes 	entries.type
#     returns = (
#         AdwInteger('SharedSetId'),
#         AdwUnicode('Name'),
#         AdwInteger('MemberCount'),
#         AdwInteger('ReferenceCount'),
#     )
#     service_name = 'get_shared_set'
#     extra_filter = 'Status IN [ENABLED]'
