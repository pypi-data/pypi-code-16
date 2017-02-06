from django.conf.urls import url

from .views import *

urlpatterns=[
            url('^$',UserList.as_view(),
                 name='user_list'),
            url('^permissions/$',UserPermissionsList.as_view()),
            url('^groups/$',UserGroupList.as_view()),
            url('^content-types/$',ContentTypeList.as_view()),
            url('^change-password/$',UserChangePassword.as_view(),
                name='change_password'),
            url('^reset-password/$',UserResetPassword.as_view(),
                name='reset_password'),
            url('^verify-email/$',UserVerifyEmail.as_view(),
                name='verify_email'),
            url('^(?P<pk>[0-9+]+)/$',UserDetail.as_view(),
                name='user_detail'),
             ]

