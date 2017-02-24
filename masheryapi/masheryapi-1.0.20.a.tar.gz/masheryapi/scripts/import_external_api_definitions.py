# -*- coding: utf-8 -*-
import sys, logging, requests
from masheryapi.services.v3.auth import Auth
from masheryapi.services.v3.base import Base
from masheryapi.services.v3.apis import Apis

class ImportExternalApiDefinitions():
    def __init__(self, mashery_v3):
        self.mashery_v3 = mashery_v3

    def get_external_contents(self, external_api_definition_source):
        try:
            return requests.get(external_api_definition_source).json()
        except ValueError as err:
            return None

    def import_definition(self, access_token, external_api_definition_source, public_domain, create_package, create_iodoc):
        api_service = Apis()

        external_api_definition_content = self.get_external_contents(external_api_definition_source)

        if external_api_definition_content == None:
            raise ValueError("External source cannot be retrieved or is invalid JSON.") 

        api_definition = api_service.from_swagger(public_domain, external_api_definition_content)

        if api_definition == None:
            raise ValueError("Problem converting external api definition.")

        imported_definition = {}

        api_response = self.mashery_v3.create(access_token, '/services', 'fields=id,name,endpoints', api_definition)

        if api_response.status_code != 200:
            imported_definition['error'] = {}
            imported_definition['error']['api'] = {}
            imported_definition['error']['api']['code'] = api_response.status_code
            imported_definition['error']['api']['message'] = api_response.json()

        else:
            created_api = api_response.json()

            imported_definition['api'] = {'id': created_api['id'], 'name': created_api['name']}

            if api_response.status_code == 200 and create_package == 'true':
                package = {'name': created_api['name'], 'plans': [{'name': created_api['name'], 'services': [created_api]}]}
                api_response = self.mashery_v3.create(access_token, '/packages', 'fields=id,name', package)
                if api_response.status_code != 200:
                    if 'error'  not in imported_definition:
                        imported_definition['error'] = {}
                    imported_definition['error']['package'] = {}
                    imported_definition['error']['package']['code'] = api_response.status_code
                    imported_definition['error']['package']['message'] = api_response.json()

                else:
                    created_package = api_response.json()
                    imported_definition['package'] = {'id': created_package['id'], 'name': created_package['name']}

            if api_create_response.status_code == 200 and create_iodoc == 'true':
                iodoc_definition = api_service.iodoc_from_swagger(public_domain, external_api_definition_content)

                iodoc = {'defaultApi': False, 'serviceId': created_api['id'], 'definition': iodoc_definition}

                api_response = self.mashery_v3.create(access_token, '/iodocs/services', '', iodoc)
                if api_response.status_code != 200:
                    if 'error'  not in imported_definition:
                        imported_definition['error'] = {}
                    imported_definition['error']['iodocs'] = {}
                    imported_definition['error']['iodocs']['code'] = api_response.status_code
                    imported_definition['error']['iodocs']['message'] = api_response.json()
                else:

                    created_iodoc = api_response.json()
                    imported_definition['iodoc'] = {'id': created_iodoc['serviceId'], 'defaultApi': created_iodoc['defaultApi']}

        return imported_definition