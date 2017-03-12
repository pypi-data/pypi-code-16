# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:  # pragma: no cover ... < Django 1.10
    class MiddlewareMixin(object):
        pass
from .conf import callback_registry
from .response import update_context_from_callbacks


__all__ = ['ContextawareProcessors']


class ContextawareProcessors(MiddlewareMixin):
    def get_registered_callbacks(self, request, response):
        return callback_registry

    def process_response(self, request, response):
        # Let ContextawareTemplateResponse handle adding and applying them,
        # if its being used.
        if hasattr(response, 'add_context_callback'):
            for callback in self.get_registered_callbacks(request, response):
                response.add_context_callback(callback)
        elif hasattr(response, 'rendering_attrs') and hasattr(response, '_request') and getattr(response, 'context_data', None) is not None and response.is_rendered is False:
            context_data = response.context_data
            new_context_data = update_context_from_callbacks(request=response._request, context=context_data,
                                                             callbacks=self.get_registered_callbacks(request, response))
            response.context_data = new_context_data
        elif hasattr(response, 'rendering_attrs') and hasattr(response, '_request') and hasattr(response, 'renderer_context') and response.is_rendered is False:
            context_data = response.renderer_context
            new_context_data = update_context_from_callbacks(request=response._request, context=context_data,
                                                             callbacks=self.get_registered_callbacks(request, response))
            response.renderer_context = new_context_data
        return response
