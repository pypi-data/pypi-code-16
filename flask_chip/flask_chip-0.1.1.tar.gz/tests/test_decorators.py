# -*- coding: utf-8 -*-

# import pytest  # type: ignore
# import six

# if six.PY3:
#     from unittest.mock import Mock, call, patch, sentinel
# else:
#     from mock import Mock, call, patch, sentinel

# from six.moves import http_client as http

# from flask import g
# from flask.views import MethodView

# from pages.tests.factories import UserFactory

# from auth import generate_token
# from auth.decorators import verify_token, logged_user


# class SpecVerifyToken(object):
#     @pytest.fixture
#     def resource(self, app):

#         class TestAPI(MethodView):
#             @verify_token
#             def get(self):
#                 return 'ok', 200

#         app.add_url_rule('/test', view_func=TestAPI.as_view('test'))

#         return app

#     @pytest.fixture
#     def client(self, resource):
#         return resource.test_client()

#     @pytest.mark.usefixtures("db")
#     def should_return_ok_when_token_is_right(self, resource, client):
#         with resource.test_request_context('/test'):
#             user = UserFactory()
#             token = generate_token(user)

#             response = client.get(
#                 '/test',
#                 content_type='application/json',
#                 headers={
#                     'X-Auth-Token': token,
#                 }
#             )

#             assert response.status_code == http.OK

#     @pytest.mark.usefixtures("db")
#     def should_user_is_set_when_token_is_right(self, resource, client):
#         with resource.test_request_context('/test'):
#             user = UserFactory()
#             token = generate_token(user)

#             client.get(
#                 '/test',
#                 content_type='application/json',
#                 headers={
#                     'X-Auth-Token': token,
#                 }
#             )

#             assert user.id == g.user.id
#             assert user.email == g.user.email

#     @pytest.mark.usefixtures("db")
#     def should_return_unauthorized_when_user_is_deactivated(self, resource, client):
#         with resource.test_request_context('/test'):
#             user = UserFactory(activated=False)
#             token = generate_token(user)

#             response = client.get(
#                 '/test',
#                 content_type='application/json',
#                 headers={
#                     'X-Auth-Token': token,
#                 }
#             )

#             assert response.status_code == http.UNAUTHORIZED

#     def should_return_unauthorized_when_token_isnt_present(self, client):
#         response = client.get(
#             '/test',
#             content_type='application/json'
#         )

#         assert response.status_code == http.UNAUTHORIZED

#     def should_return_unauthorized_when_token_is_wrong(self, client):
#         response = client.get(
#             '/test',
#             content_type='application/json',
#             headers={
#                 'X-Auth-Token': 'wrong token'
#             }
#         )

#         assert response.status_code == http.UNAUTHORIZED


# class SpecLoggedUser(object):
#     @pytest.fixture
#     def resource(self, app):

#         class TestAPI(MethodView):
#             @logged_user
#             def get(self):
#                 return 'ok', 200

#         app.add_url_rule('/test', view_func=TestAPI.as_view('test'))

#         return app

#     @pytest.fixture
#     def client(self, resource):
#         return resource.test_client()

#     @pytest.mark.usefixtures("db")
#     def should_set_user_to_global(self, resource, client):
#         with resource.test_request_context('/test'):
#             user = UserFactory()
#             token = generate_token(user)

#             client.get(
#                 '/test',
#                 content_type='application/json',
#                 headers={
#                     'X-Auth-Token': token,
#                 }
#             )

#             assert user.id == g.user.id
#             assert user.email == g.user.email

#     @pytest.mark.usefixtures("db")
#     def should_set_user_to_none_when_token_isnt_present(self, resource, client):
#         with resource.test_request_context('/test'):
#             client.get(
#                 '/test',
#                 content_type='application/json',
#             )

#             assert g.user is None
