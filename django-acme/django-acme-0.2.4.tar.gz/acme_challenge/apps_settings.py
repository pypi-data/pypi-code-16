# -*- coding: utf-8
from __future__ import unicode_literals, absolute_import

import os

from django.conf import settings

ACME_CHALLENGE_URL_SLUG = getattr(settings, 'ACME_CHALLENGE_URL_SLUG',
                                  os.getenv('ACME_CHALLENGE_URL_SLUG', ''))
ACME_CHALLENGE_TEMPLATE_CONTENT = getattr(settings, 'ACME_CHALLENGE_TEMPLATE_CONTENT',
                                          os.getenv('ACME_CHALLENGE_TEMPLATE_CONTENT', ''))
