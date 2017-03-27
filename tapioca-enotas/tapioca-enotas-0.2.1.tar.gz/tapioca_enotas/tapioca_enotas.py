# coding: utf-8

from tapioca import (
    TapiocaAdapter, generate_wrapper_from_adapter, JSONAdapterMixin)

from .auth import HTTPENotasBasicAuth
from .resource_mapping import RESOURCE_MAPPING


class EnotasClientAdapter(JSONAdapterMixin, TapiocaAdapter):
    api_root = 'https://api.enotasgw.com.br/v1'
    resource_mapping = RESOURCE_MAPPING

    def get_request_kwargs(self, api_params, *args, **kwargs):
        params = super(EnotasClientAdapter, self).get_request_kwargs(
            api_params, *args, **kwargs)

        params['auth'] = HTTPENotasBasicAuth(api_params.get('token'))
        params['headers']['Content-Type'] = 'application/json'

        return params

    def get_iterator_list(self, response_data):
        return response_data

    def get_iterator_next_request_kwargs(self, iterator_request_kwargs,
                                         response_data, response):
        pass


Enotas = generate_wrapper_from_adapter(EnotasClientAdapter)
