# -*- coding: utf-8 -*-
import json
import logging

from csp_report.utils import write_csp_report, write_cleaned_csp_report
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from csp_report.models import CSPReport

logger = logging.getLogger('django.request')


def get_important_request_meta(headers, important_headers=None):
    if not important_headers:
        important_headers = [
            'HTTP_USER_AGENT',
            'HTTP_X_FORWARDED_FOR',
            'HTTP_X_REAL_IP',
            'REMOTE_ADDR',
            'HTTP_ORIGIN',
            'HTTP_CACHE_CONTROL',
            'SERVER_NAME',
        ]
    return {k: v for k, v in headers.items() if k in important_headers}


def process_scp_report(data, **kwargs):
    request_meta = kwargs.get('request_meta', {})
    report_data = dict(
        host=kwargs.get('host', ''),
        document_uri=data['document-uri'],
        blocked_uri=data['blocked-uri'],
        referrer=data.get('referrer', ''),
        body=data,
        request_meta=get_important_request_meta(request_meta),
    )

    report = write_csp_report(report_data)

    if report:
        write_cleaned_csp_report(report, report_data)


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
