from csp_report.models import CSPReport
from django.conf import settings

BLOCKED_URL_FILTERS = [
    {'type': 'equals', 'value': 'data'},
    {'type': 'equals', 'value': 'asset'},
]


def write_csp_report(report_data):
    return CSPReport.objects.create(**report_data)


def write_cleaned_csp_report(report, report_data):
    csp_blocked_url_filters = getattr(settings, 'CSP_BLOCKED_URL_FILTERS', BLOCKED_URL_FILTERS)

    for _ in csp_blocked_url_filters:
        filter_type, filter_value = _['type'], _['value']
        if filter_type == 'equals':
            if report_data.get('blocked_uri') == filter_value:
                return
        elif filter_type == 'startswith':
            if report_data.get('blocked_uri', '').startswith() == filter_value:
                return
