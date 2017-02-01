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
                return HttpResponse("OK", status=202)

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
            )

        return response
