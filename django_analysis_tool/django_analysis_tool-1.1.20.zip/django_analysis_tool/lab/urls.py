
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from lab_analysis_tools import views
admin.autodiscover()

# urlpatterns = patterns('',
#         (r'^lab_analysis_tools/', include('lab_analysis_tools.urls')),
#         (r'^$', 'lab_analysis_tools.views.index'),
#         (r'^admin/', include(admin.site.urls)),
#
# ) + static(settings.JSON_URL, document_root=settings.JSON_ROOT)


urlpatterns = [
        url(r'^lab_analysis_tools/', include('lab_analysis_tools.urls')),
        url(r'^$', views.index),
        url('^admin/', include(admin.site.urls))
] + static(settings.JSON_URL, document_root=settings.JSON_ROOT)


