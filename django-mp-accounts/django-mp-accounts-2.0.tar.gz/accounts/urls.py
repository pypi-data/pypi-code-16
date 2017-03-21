
from django.conf.urls import url
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required

from accounts import views


urlpatterns = [

    url(r'^profile/$', login_required(TemplateView.as_view(
        template_name='account/profile/index.html')), name='profile'),

    url(r'^edit/$', views.ProfileUpdateView.as_view(), name='edit'),

    url(r'^remove/$', views.RemoveProfileView.as_view(), name='remove'),

]
