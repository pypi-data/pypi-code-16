# -*- coding: utf-8 -*-
from congo.utils.classes import MetaData
from congo.utils.decorators import staff_required, secure_allowed
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http.response import HttpResponseRedirect, Http404
from django.shortcuts import render
from django.template import loader
from django.template.context import Context
from django.utils.module_loading import import_string
from django.utils.translation import ugettext_lazy as _
import logging
import os

@staff_required
def reset_server(request):
    logger = logging.getLogger('system.reset_server')
    message = _(u"Reset serwera")
    command = "/bin/kill -9 -1"

    extra = {
        'user': request.user,
        'extra_info': command
    }

    logger.info(message, extra = extra)
    os.system(command)

    meta = MetaData(request, message)

    extra_context = {
        'meta': meta,
    }

    return render(request, 'congo/maintenance/reset_server.html', extra_context)

@secure_allowed
def redirect(request, content_type_id, object_id):
    try:
        obj = ContentType.objects.get_for_id(content_type_id).get_object_for_this_type(id = object_id)
        if hasattr(obj, 'get_absolute_url'):
            url = obj.get_absolute_url()
            return HttpResponseRedirect(url)
    except ObjectDoesNotExist:
        pass
    raise Http404()

@secure_allowed
def http_error(request, error_no):
    error_dict = {
        400: {
            'title': _(u"Złe zapytanie"),
            'description': _(u"Niestety Twoje zapytanie wydaje się być złe i nie może być przetworzone."),
            'http_response': 'django.http.HttpResponseBadRequest',
        },
        403: {
            'title': _(u"Odmowa dostępu"),
            'description': _(u"Niestety dostęp do miejsca, którego szukasz jest zablokowany."),
            'http_response': 'django.http.HttpResponseForbidden',
        },
        404: {
            'title': _(u"Strona nie została znaleziona"),
            'description': _(u"Niestety strona, której szukasz nie została odnaleziona. Prawdopodobnie została usunięta z powodu wygaśnięcia"),
            'http_response': 'django.http.HttpResponseNotFound',
        },
        500: {
            'title': _(u"Wewnętrzny błąd serwera"),
            'description': _(u"Wystąpił wewnętrzny błąd serwera. Robimy co w naszej mocy, aby rozwiązać problem. Przepraszamy za wszelkie niedogodności."),
            'http_response': 'django.http.HttpResponseServerError',
        },
        503: {
            'title': _(u"Serwis jest tymczasowo niedostępny"),
            'description': _(u"Planowana przebudowa strony jest w toku. Przepraszamy za wszelkie niedogodności. Prosimy przyjść później."),
            'http_response': 'congo.utils.http.HttpResponseServiceUnavailable',
        },
    }

    meta = MetaData(request, error_dict[error_no]['title'])

    context = {
        'meta' : meta,
        'description': error_dict[error_no]['description'],
    }

    template = loader.get_template('congo/maintenance/http_error.html')
    HttpResponse = import_string(error_dict[error_no]['http_response'])
    return HttpResponse(template.render(Context(context)))

@secure_allowed
def bad_request(request):
    return http_error(request, 400)

@secure_allowed
def permission_denied(request):
    return http_error(request, 403)

@secure_allowed
def page_not_found(request):
    return http_error(request, 404)

@secure_allowed
def server_error(request):
    return http_error(request, 500)

@secure_allowed
def service_unavailable(request):
    return http_error(request, 503)
