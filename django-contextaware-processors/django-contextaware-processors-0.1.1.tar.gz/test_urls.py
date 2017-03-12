# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import get_user_model
try:
    from rest_framework import serializers
    from rest_framework.response import Response
    from rest_framework.views import APIView
except ImportError:
    pre_urlpatterns = []
else:
    class UserSerializer(serializers.ModelSerializer):
        class Meta:
            model = get_user_model()
            fields = ( 'username', 'email',)

    class ExampleDRFView(APIView):
        def get_object(self, pk):
            return get_user_model().objects.get(pk=pk)

        def get(self, request, pk, format=None):
            obj = self.get_object(pk)
            serializer = UserSerializer(obj, context={'request': request})
            return Response(serializer.data)


    drf_user_url = url(r'^drf_user/(?P<pk>[0-9]+)/$', ExampleDRFView.as_view(),
                       name='drf_user')
    pre_urlpatterns = [drf_user_url]

main_urlpatterns = [
    url('^', include(admin.site.urls)),
]
urlpatterns = pre_urlpatterns + main_urlpatterns

