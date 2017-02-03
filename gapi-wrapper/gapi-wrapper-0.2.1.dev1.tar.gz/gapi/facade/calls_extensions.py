# -*- coding: utf-8 -*-
from gapi.facade.calls_criterions import GetCriterionsBase
from gapi.facade.result_fields import (AdwField, AdwANSI, AdwInteger)


class AdwExtensionDict(AdwField):

    def _to_plain(self):
        return list(self.value)


class GetExtensionsBase(GetCriterionsBase):
    returns = (
        AdwANSI('ExtensionType'),
        AdwExtensionDict('Extensions', obtain_name='extensionSetting.extensions', output_name='extensions'),
    )


class GetCampaignExtensions(GetExtensionsBase):
    returns = GetExtensionsBase.returns + (
        AdwInteger('CampaignId'),
    )
    service_name = 'get_campaign_extensions'


class GetAdGroupExtensions(GetExtensionsBase):
    returns = GetExtensionsBase.returns + (
        AdwInteger('CampaignId'),
        AdwInteger('AdGroupId'),
    )
    service_name = 'get_ad_group_extensions'


class GetCustomerExtensions(GetExtensionsBase):
    service_name = 'get_customer_extensions'