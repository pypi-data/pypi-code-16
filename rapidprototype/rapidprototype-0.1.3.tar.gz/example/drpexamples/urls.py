from django.conf.urls import url
import views

urlpatterns = [
    url(r'^example/placeholder/$', views.placeholder_image_example_view),
]
