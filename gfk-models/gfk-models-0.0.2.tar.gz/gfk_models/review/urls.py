from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^reviews/add$', views.ReviewCreateView.as_view(), name='add'),
    url(r'^migrate$', views.migrate_to_new_reviews),
]