from jsonapi_mock_server.base_views import ResourceViewSet


from resources import QuestionResource


class QuestionViewSet(QuestionResource, ResourceViewSet):
    pass
