from facebookads.adobjects.objectparser import ObjectParser
from facebookads.api import FacebookRequest
from facebookads.objects import Business
from facebookads.typechecker import TypeChecker


class BusinessWrap(Business):

    def __init__(self, fbid=None, parent_id=None, api=None):
        self._isBusinessWrap = True
        super(BusinessWrap, self).__init__(fbid, parent_id, api)

    def get_ad_accounts(self, fields=None, params=None, batch=None, pending=False):
        from facebookads.adobjects.adaccount import AdAccount
        param_types = {
        }
        enums = {
        }
        request = FacebookRequest(
            node_id=self['id'],
            method='GET',
            endpoint='/adaccounts',
            api=self._api,
            param_checker=TypeChecker(param_types, enums),
            target_class=AdAccount,
            api_type='EDGE',
            response_parser=ObjectParser(target_class=AdAccount),
        )
        request.add_params(params)
        request.add_fields(fields)

        if batch is not None:
            request.add_to_batch(batch)
            return request
        elif pending:
            return request
        else:
            self.assure_call()
            return request.execute()