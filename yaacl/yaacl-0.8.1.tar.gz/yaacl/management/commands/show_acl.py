# -*- coding:utf-8 -*-
from django.core.management.base import BaseCommand
from django.utils.translation import ugettext_lazy as _

from yaacl.models import ACL

__author__ = 'Daniel Alkemic Czuba <dc@danielczuba.pl>'


class Command(BaseCommand):
    help = _('Lists all saved resources')

    def handle(self, *args, **options):
        for acl in ACL.objects.all():
            self.stdout.write('Resource: %s, displayed named: %s' % (
                acl.resource,
                acl.display,
            ))
