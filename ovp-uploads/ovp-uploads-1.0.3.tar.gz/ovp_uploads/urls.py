from django.conf.urls import url, include
from rest_framework import routers

from ovp_uploads import views

router = routers.DefaultRouter()
router.register(r'uploads/images', views.UploadedImageViewSet, 'upload-images')

urlpatterns = [
  url(r'^', include(router.urls)),
]
