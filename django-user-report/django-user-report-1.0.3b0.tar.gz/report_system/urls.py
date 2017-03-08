from django.conf.urls import url, include
from report_system import views

urlpatterns = [
    url(r'^(?P<target_model>[-\w]+)/(?P<id>\d+)/$', views.CreateTicketView.as_view(),
        name="ticket_create_api"),
]