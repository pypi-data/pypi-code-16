from django.conf.urls import include, url

from rest_framework import routers

from .serializers.debt import DebtViewSet
from .serializers.feature import FeatureViewSet
from .serializers.profile import ProfileViewSet
from .serializers.user import UserViewSet
from .views.control_panel import ControlPanelView
from .views.dashboard import DashboardView
from .views.story_create import StoryCreate
from .views.story_detail import StoryDetail
from .views.story_history import StoryHistory
from .views.story_list import StoryList

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'profiles', ProfileViewSet)
router.register(r'debts', DebtViewSet)
router.register(r'features', FeatureViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^$', DashboardView.as_view(), name='dashboard'),
    url(r'^control_panel/$', ControlPanelView.as_view(), name='control_panel'),
    url(r'^api/', include(router.urls), name='rootapi'),
    url(r'^api-auth/', include('rest_framework.urls')),
    url(r'^stories/$', StoryList.as_view(), name='stories'),
    url(
        r'^(?P<ident>D|F)(?P<pk>[0-9]+)/$', StoryDetail.as_view(),
        name='story_detail'
    ),
    url(
        r'^new/(?P<story_type>debt|feature)/$', StoryCreate.as_view(),
        name='story_create'
    ),
    url(
        r'^(?P<ident>D|F)(?P<pk>[0-9]+)/history/$', StoryHistory.as_view(),
        name='story_history'
    ),
]
