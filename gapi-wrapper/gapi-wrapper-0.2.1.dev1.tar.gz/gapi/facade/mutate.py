# -*- coding: utf-8 -*-
from gapi.facade.calls import FacadeCalls, SingleObjectFacadeCall
from gapi.facade.result_fields import AdwInteger, AdwANSI, AdwObject, AdwBoolean, AdwUnicode


class Operations(object):

    def __init__(self):
        self.data = []

    def _append(self, operator, operand):
        self.data.append(dict(
                operator=operator,
                operand=operand
            ))

    def __add__(self, operand):
        self._append('ADD', operand)
        return self

    def __or__(self, operand):
        self._append('SET', operand)
        return self

    def __sub__(self, operand):
        self._append('REMOVE', operand)
        return self

    def __iadd__(self, operand):
        return self + operand

    def __ior__(self, operand):
        return self | operand

    def __isub__(self, operand):
        return self - operand

    def to_list(self):
        return [self._check_operand(operand) for operand in self.data]

    def _check_operand(self, operand, deep=1):
        deep += 1
        if deep > 100:
            raise ValueError('Operations: too deep check operand! May be cyclic references...')
        if isinstance(operand, Operand):
            return self._check_operand(operand.to_dict())
        if isinstance(operand, dict):
            return {k: self._check_operand(v, deep) for k, v in operand.iteritems()}
        if isinstance(operand, list):
            return [self._check_operand(v, deep) for v in operand]
        if isinstance(operand, set):
            return {self._check_operand(v, deep) for v in operand}
        return operand


class Operand(object):

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def to_dict(self):
        return self.kwargs


class XsiTypeOperand(Operand):

    def to_dict(self):
        criterion = dict(xsi_type=self.get_xsi_type())
        criterion.update(**self.kwargs)
        return criterion

    def get_xsi_type(self):
        return self.__class__.__name__.replace('Criterion', '')


class FullNameXsiTypeOperand(XsiTypeOperand):

    def get_xsi_type(self):
        return self.__class__.__name__


class CampaignCriterion(FullNameXsiTypeOperand):
    pass


class NegativeCampaignCriterion(FullNameXsiTypeOperand):
    pass


class BiddableAdGroupCriterion(FullNameXsiTypeOperand):
    pass


class KeywordCriterion(XsiTypeOperand):
    pass


class PlacementCriterion(XsiTypeOperand):
    pass


class CpcBid(FullNameXsiTypeOperand):
    pass


class MutateAdsPause(FacadeCalls):
    params = dict(ad_group_id=None, ad_ids=None, status='PAUSED')
    returns = (
            AdwInteger('Id', obtain_name='ad.id'),
            AdwInteger('AdGroupId'),
            AdwANSI('Status'),
            AdwObject('Error'),
    )

    def handle(self):
        ad_group_id = self._get_param('ad_group_id')
        status = self._get_param('status')
        operations = Operations()
        for ad_id in self._get_param('ad_ids'):
            operand = Operand(
                adGroupId=ad_group_id,
                ad={'id': ad_id, },
                status=status
            )
            operations |= operand
        result = self.service.mutate('AdGroupAdService', operations.to_list())
        return result


class MutateCampaignMinusKeywords(FacadeCalls):
    params = dict(campaign_id=None, keywords=None)
    returns = (
        AdwInteger('CampaignId'),
        AdwBoolean('isNegative'),
        AdwUnicode('keyword', obtain_name='criterion.text'),
        AdwInteger('CriterionId', obtain_name='criterion.id'),
        AdwObject('Error'),
    )

    def handle(self):
        campaign_id = self._get_param('campaign_id')
        keywords = self._get_param('keywords')
        operations = Operations()
        for kw in keywords:
            criterion = NegativeCampaignCriterion(
                campaignId=campaign_id,
                criterion=KeywordCriterion(
                    matchType='EXACT',
                    text=kw),
            )
            operations += criterion
        result = self.service.mutate('CampaignCriterionService', operations.to_list())
        return result


class MutateCampaignNegativePlacement(FacadeCalls):
    params = dict(campaign_id=None, url=None)
    returns = (
        AdwInteger('CampaignId'),
        AdwBoolean('isNegative'),
        AdwUnicode('url', obtain_name='criterion.url'),
        AdwInteger('CriterionId', obtain_name='criterion.id'),
        AdwObject('Error'),
    )

    def handle(self):
        campaign_id = self._get_param('campaign_id')
        url = self._get_param('url')
        criterion = NegativeCampaignCriterion(
            campaignId=campaign_id,
            criterion=PlacementCriterion(url=url),
        )
        operations = Operations() + criterion
        result = self.service.mutate('CampaignCriterionService', operations.to_list())
        return result


class MutateKeywordBidSingle(SingleObjectFacadeCall):
    params = dict(keyword_bid=None)
    returns = (
        AdwInteger('AdGroupId'),
        AdwInteger('KeywordId', obtain_name='criterion.id'),
    )
    #{
    #    adGroupId = 20202374729
    #    criterion =
    #       (Keyword){
    #          id = 8636149750
    #          type = "KEYWORD"
    #          Criterion.Type = "Keyword"
    #          text = "коттеджный поселок чистые пруды 2"
    #          matchType = "BROAD"
    #       }
    #    AdGroupCriterion.Type = "BiddableAdGroupCriterion"
    #    userStatus = "ENABLED"
    #    systemServingStatus = "ELIGIBLE"
    #    approvalStatus = "APPROVED"
    #    biddingStrategyConfiguration =
    #       (BiddingStrategyConfiguration){
    #          biddingStrategyType = "MANUAL_CPC"
    #          biddingStrategySource = "CRITERION"
    #          biddingScheme =
    #             (ManualCpcBiddingScheme){
    #                BiddingScheme.Type = "ManualCpcBiddingScheme"
    #                enhancedCpcEnabled = False
    #             }
    #          bids[] =
    #             (CpmBid){
    #                Bids.Type = "CpmBid"
    #                bid =
    #                   (Money){
    #                      ComparableValue.Type = "Money"
    #                      microAmount = 7000000
    #                   }
    #                cpmBidSource = "ADGROUP"
    #             },
    #             (CpcBid){
    #                Bids.Type = "CpcBid"
    #                bid =
    #                   (Money){
    #                      ComparableValue.Type = "Money"
    #                      microAmount = 3000000
    #                   }
    #                cpcBidSource = "CRITERION"
    #             },
    #       }
    #  }

    def handle(self):
        keyword_bid = self._get_param('keyword_bid')
        micro_amount = str(int(float(keyword_bid['amount']) * 1000000.0))  # TODO надо бы спец класс поля запилить
        bid = CpcBid(bid=dict(microAmount=micro_amount))
        criterion = BiddableAdGroupCriterion(
            adGroupId=str(keyword_bid['ad_group_id']),
            criterion=dict(id=str(keyword_bid['keyword_id'])),
            biddingStrategyConfiguration=dict(bids=[bid, ])
        )
        operations = Operations() | criterion
        result = self.service.mutate_single('AdGroupCriterionService', operations.to_list()[0])
        return result
