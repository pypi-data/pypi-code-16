from rest_framework import routers

from joda_misc import views

router = routers.SimpleRouter(trailing_slash=False)
router.register(r'misc-documents', views.MiscDocumentsViewSet, base_name='misc-documents')
router.register(r'misc-types', views.MiscTypesViewSet)
