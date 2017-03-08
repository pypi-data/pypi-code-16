from django.conf.urls import  url, include
from indaba.talks.views import (CreateTalk, TalkView, )

urlpatterns = [
    url(r'^submit_talk', CreateTalk.as_view(), name='create_talks'),
    url(r'^(?P<pk>\d+)/$', TalkView.as_view(), name='pyladies_talk'),
    ]
        
