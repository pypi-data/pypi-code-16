from django.conf import settings


# Default pagination limit
COMMON_PAGINATOR_PAGINATE_BY = getattr(settings, 'COMMON_PAGINATOR_PAGINATE_BY', 10)