"""
Some testing tools that coop projects can use.

Most projects will want to do something like:

.. code-block:: python

    from coop.test import TestAllTheThingsMixin
    from django.test import TestCase

    class TestAllTheThings(TestAllTheThingsMixin, TestCase):
        pass
"""
from io import StringIO
from unittest import mock
from urllib.parse import urlsplit

from django.conf import settings
from django.contrib.staticfiles import finders
from django.core.management import call_command
from wagtail.wagtailimages.tests.utils import get_test_image_file

from coop.utils import testdata


class CoopAssertionMixin():
    def assertNoMissingMigrations(self):
        try:
            out = StringIO()
            call_command(
                *'makemigrations --check --dry-run --no-color --name=missing_migration'.split(),
                stdout=out)
        except SystemExit:
            out.seek(0)
            self.fail(msg='Missing migrations:\n\n' + out.read())

    def assertTestdataWorks(self):
        """
        Run the ``testdata`` management command. The tests pass if no errors
        are thrown
        """
        def mocked_download_image(image_path, image_url):
            """
            Don't actually go and download the image from lorem pixel, as that
            is quite slow, but still make an image file in the correct place.
            """
            test_image = get_test_image_file(image_path)
            with open(image_path, 'wb') as f:
                test_image.file.seek(0)
                f.write(test_image.file.read())

        with mock.patch.object(testdata, 'download_image_file', mocked_download_image):
            call_command('testdata', stdout=StringIO())
            call_command('update_index', stdout=StringIO())

    def assertStandardFilesExist(self):
        for standard_file in ['/favicon.ico', '/robots.txt', '/humans.txt']:
            response = self.client.get(standard_file, follow=True)
            final_url = response.redirect_chain[-1][0]
            path = urlsplit(final_url).path
            self.assertTrue(path.startswith(settings.STATIC_URL))
            tail = path[len(settings.STATIC_URL):]
            self.assertTrue(finders.find(tail))

    def assert404PageRenders(self):
        url = '/quite/likely/not/a/page/'
        response = self.client.get(url)
        self.assertContains(response, url, status_code=404)

    def assert500PageRenders(self):
        response = self.client.get('/500/')
        self.assertEqual(response.status_code, 500)


class TestAllTheThingsMixin(CoopAssertionMixin):
    """
    Run all the stand-alone assertions that check for a coop project in a good
    state.
    """
    def test_migrations(self):
        self.assertNoMissingMigrations()

    def test_testdata(self):
        self.assertTestdataWorks()

    def test_standard_files_exist(self):
        self.assertStandardFilesExist()

    def test_error_pages(self):
        self.assert404PageRenders()
        self.assert500PageRenders()
