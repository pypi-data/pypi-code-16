from django.conf.urls import url

from .views import NoticeSettingsView


urlpatterns = [
    url(r"^settings/$", NoticeSettingsView.as_view(), name="notification_notice_settings"),
]
