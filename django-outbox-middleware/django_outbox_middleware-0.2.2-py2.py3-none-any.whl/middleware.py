from django.conf import settings
from django.http import HttpResponse

try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object

from .models import OutboxRequestLog


class OutboxMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if 'HTTP_OUTBOX_REQUEST_UUID' in request.META:
            if OutboxRequestLog.objects.filter(
                request_uuid=request.META['HTTP_OUTBOX_REQUEST_UUID'],
                response_status_code__lt=400
            ).exists():
                resp = HttpResponse("OK", status=202)
                resp['Outbox-Flagged-Duplicate'] = True
                return resp

            # If logging the body, access it before it's sent to the view so
            # that calling `request.read()` in the view doesn't break the
            # middleware. See https://goo.gl/FUOVrV
            if getattr(settings, 'OUTBOX_LOG_BODY', False):
                str(request.body)

    def process_response(self, request, response):
        if 'HTTP_OUTBOX_REQUEST_UUID' in request.META:

            if getattr(settings, 'OUTBOX_LOG_BODY', False):
                request_body = request.body
            else:
                request_body = None

            OutboxRequestLog.objects.create(
                request_uuid=request.META['HTTP_OUTBOX_REQUEST_UUID'],
                response_status_code=response.status_code,
                request_body=request_body,
                request_path=request.get_full_path(),
                request_flagged_duplicate=response.get('Outbox-Flagged-Duplicate', False),
            )

        return response
