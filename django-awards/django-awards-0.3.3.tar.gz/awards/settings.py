from django.conf import settings


IMAGE_URL = getattr(settings, 'AWARDS_IMAGE_URL', 'icons/awards/{slug}.png')
