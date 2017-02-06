from urllib.parse import urlparse
from csp_report.models import CSPReport, CleanedCSPReport
from django.conf import settings

BLOCKED_URL_FILTERS = [
    {'type': 'equals', 'value': 'data'},
    {'type': 'equals', 'value': 'asset'},
]


def write_csp_report(report_data):
    return CSPReport.objects.create(**report_data)


def write_cleaned_csp_report(report):
    csp_blocked_url_filters = getattr(settings, 'CSP_BLOCKED_URL_FILTERS', BLOCKED_URL_FILTERS)

    for _ in csp_blocked_url_filters:
        filter_type, filter_value = _['type'], _['value']
        if filter_type == 'equals':
            if report.blocked_uri == filter_value:
                return
        elif filter_type == 'startswith':
            if report.blocked_uri.startswith() == filter_value:
                return

    parse_document_uri = urlparse(report.document_uri)
    parse_blocked_uri = urlparse(report.blocked_uri)

    report_data = {
        'report': report,
        'document_scheme': parse_document_uri.scheme,
        'document_domain': parse_document_uri.netloc,
        'document_path': parse_document_uri.path,
        'document_query': parse_document_uri.query,
        'blocked_domain': parse_blocked_uri.netloc,
        'blocked_url': parse_blocked_uri.path + parse_blocked_uri.query,
    }

    return CleanedCSPReport.objects.create(**report_data)


