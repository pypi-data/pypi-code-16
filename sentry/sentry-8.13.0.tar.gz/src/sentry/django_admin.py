from __future__ import absolute_import

from copy import copy
from django.contrib import admin


class RestrictiveAdminSite(admin.AdminSite):
    def has_permission(self, request):
        return request.is_superuser()


def make_site():
    admin.autodiscover()

    # now kill off autodiscover since it would reset the registry
    admin.autodiscover = lambda: None

    site = RestrictiveAdminSite()
    # copy over the autodiscovery
    site._registry = copy(admin.site._registry)

    # clear the default site registry to avoid leaking an insecure admin
    admin.site._registry = {}

    # rebind our admin site to maintain compatibility
    admin.site = site

    return site


site = make_site()
