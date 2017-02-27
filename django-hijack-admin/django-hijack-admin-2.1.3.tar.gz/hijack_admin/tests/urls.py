"""URLs to run the tests."""
from compat import include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url(r'^hijack/', include('hijack.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^hello/', include('hijack.tests.test_app.urls'))
]
