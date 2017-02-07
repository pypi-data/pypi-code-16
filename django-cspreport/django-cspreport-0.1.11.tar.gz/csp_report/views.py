# -*- coding: utf-8 -*-
import json
import logging

from csp_report.utils import process_scp_report
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


logger = logging.getLogger('django.request')


@require_http_methods(['POST'])
@csrf_exempt
def csp_report_view(request):
    try:
        data = json.loads(request.body.decode())['csp-report']
        logger.debug(data)
        logger.debug(request.META)
        host = request.META.get('HTTP_HOST')
        process_scp_report(data, host=host, request_meta=dict(request.META))
    except KeyError:
        return HttpResponse(status=422)

    return HttpResponse(content='ok')
