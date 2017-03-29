from facebookads.adobjects.objectparser import ObjectParser
from facebookads.api import FacebookRequest
from facebookads.objects import AdAccount, AbstractCrudObject
from facebookads.typechecker import TypeChecker


class AdAccountWrap(AdAccount):

    def __init__(self, fbid=None, parent_id=None, api=None):
        self._isAdAccountWrap = True
        super(AdAccountWrap, self).__init__(fbid, parent_id, api)

    def add_agency(self, fields=None, params=None, batch=None, pending=False):
        param_types = {
            'business': 'string',
            'permitted_roles': 'list<permitted_roles_enum>'
        }
        enums = {
            'permitted_roles_enum': AdAccount.PermittedRoles.__dict__.values()
        }
        request = FacebookRequest(
            node_id=self['id'],
            method='POST',
            endpoint='/agencies',
            api=self._api,
            param_checker=TypeChecker(param_types, enums),
            target_class=AbstractCrudObject,
            api_type='NODE',
            response_parser=ObjectParser(target_class=AbstractCrudObject),
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

    def remove_agency(self, fields=None, params=None, batch=None, pending=False):
        param_types = {
            'business': 'string'
        }
        enums = {
        }
        request = FacebookRequest(
            node_id=self['id'],
            method='DELETE',
            endpoint='/agencies',
            api=self._api,
            param_checker=TypeChecker(param_types, enums),
            target_class=AbstractCrudObject,
            api_type='NODE',
            response_parser=ObjectParser(target_class=AbstractCrudObject),
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

    def get_userpermissions(self, fields=None, params=None, batch=None, pending=False):
        param_types = {

        }
        enums = {
        }
        request = FacebookRequest(
            node_id=self['id'],
            method='GET',
            endpoint='/userpermissions',
            api=self._api,
            param_checker=TypeChecker(param_types, enums),
            target_class=AbstractCrudObject,
            api_type='NODE',
            response_parser=ObjectParser(target_class=AbstractCrudObject),
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

    def create_userpermissions(self, fields=None, params=None, batch=None, pending=False):
        param_types = {
            'business': 'string',
            'user': 'string',
            'role': 'role_enum'
        }
        enums = {
            'role_enum': [
                'ADMIN',
                'GENERAL_USER',
                'REPORTS_ONLY'
            ],
        }
        request = FacebookRequest(
            node_id=self['id'],
            method='POST',
            endpoint='/userpermissions',
            api=self._api,
            param_checker=TypeChecker(param_types, enums),
            target_class=AbstractCrudObject,
            api_type='NODE',
            response_parser=ObjectParser(target_class=AbstractCrudObject),
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

    def delete_userpermissions(self, fields=None, params=None, batch=None, pending=False):
        param_types = {
            'business': 'string',
            'user': 'string',
        }
        enums = {
        }
        request = FacebookRequest(
            node_id=self['id'],
            method='DELETE',
            endpoint='/userpermissions',
            api=self._api,
            param_checker=TypeChecker(param_types, enums),
            target_class=AbstractCrudObject,
            api_type='NODE',
            response_parser=ObjectParser(target_class=AbstractCrudObject),
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
