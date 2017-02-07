from django.conf.urls import url
from rest_framework.routers import SimpleRouter

from sample_mock_server import views


router = SimpleRouter(trailing_slash=False)
router.register(r'questions', views.QuestionViewSet, base_name='question')
urlpatterns = router.urls
#urlpatterns = [
#    url(r'^admin/', admin.site.urls),
#]
