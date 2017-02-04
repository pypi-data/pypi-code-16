# -*- coding:utf-8 -*-
from django.core.management.base import BaseCommand
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from yaacl.models import ACL

__author__ = 'Daniel Alkemic Czuba <dc@danielczuba.pl>'


class Command(BaseCommand):
    help = _('Sync resources with database')

    def handle(self, *args, **options):
        for app in settings.INSTALLED_APPS:
            try:
                __import__("%s.views" % app)
            except ImportError:
                pass

        existing_resources = set([
            resource_name
            for resource_name, display_name in ACL.acl_list.items()
        ])
        saved_resources = set([
            acl.resource
            for acl in ACL.objects.all()
        ])

        # resources to remove
        for resource_name in saved_resources - existing_resources:
            ACL.objects.filter(resource=resource_name).delete()
            self.stdout.write('Deleted resource: %s' % resource_name)

        # resources to add
        for resource_name in existing_resources - saved_resources:
            ACL.objects.create(
                resource=resource_name,
                display=ACL.acl_list[resource_name],
            )
            self.stdout.write('Added resource: %s' % resource_name)

        for resource_name in existing_resources & saved_resources:
            entry = ACL.objects.get(resource=resource_name)
            if entry.display != ACL.acl_list[resource_name]:
                entry.display = ACL.acl_list[resource_name]
                entry.save()
                self.stdout.write('Updated resource: %s' % resource_name)
