# -*- coding: utf-8 -*-
import os
from django.core.management.base import BaseCommand
from django.db.models import signals
from django.db.utils import IntegrityError

from i18nize.client import Client
from django.conf import settings

import os


class Command(BaseCommand):

    def handle(self, *args, **options):
        client = Client(**settings.DJANGO_I18NIZE_CONFIG)
        client.get_all_locales()