from __future__ import absolute_import, unicode_literals

from . import MAYAN_VERSION


if MAYAN_VERSION[0:2] <= (2, 1):
    from django.contrib.auth import get_user_model
    from django.test import override_settings

    from common.tests.test_views import GenericViewTestCase
    from documents.models import DocumentType
    from documents.tests.literals import TEST_DOCUMENT_TYPE
    from user_management.tests import TEST_USER_USERNAME, TEST_USER_PASSWORD

    from ..tests.literals import TEST_SMALL_DOCUMENT_PATH

    @override_settings(OCR_AUTO_OCR=False)
    class GenericDocumentViewTestCase(GenericViewTestCase):
        def setUp(self):
            super(GenericDocumentViewTestCase, self).setUp()
            self.document_type = DocumentType.objects.create(
                label=TEST_DOCUMENT_TYPE
            )

            with open(TEST_SMALL_DOCUMENT_PATH) as file_object:
                self.document = self.document_type.new_document(
                    file_object=file_object
                )

        def tearDown(self):
            super(GenericDocumentViewTestCase, self).tearDown()
            if self.document_type.pk:
                self.document_type.delete()

        def grant(self, permission):
            self.role.permissions.add(
                permission.stored_permission
            )

        def login(self, username, password):
            logged_in = self.client.login(username=username, password=password)

            user = get_user_model().objects.get(username=username)

            self.assertTrue(logged_in)
            self.assertTrue(user.is_authenticated())

        def login_user(self):
            self.login(username=TEST_USER_USERNAME, password=TEST_USER_PASSWORD)
else:
    from documents.tests.test_views import GenericDocumentViewTestCase
