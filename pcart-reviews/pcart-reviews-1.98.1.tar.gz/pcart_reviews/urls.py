from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^form/$', views.review_form, name='review-form'),
]

