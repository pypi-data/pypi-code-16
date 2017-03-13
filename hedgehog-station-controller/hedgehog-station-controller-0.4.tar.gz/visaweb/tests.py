from django.test import TestCase
import datetime
from django.utils import timezone

# Create your tests here.

from .models import VisaDevice, VisaEvent


class VisaDeviceMethodTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() should return False for questions whose
        pub_date is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)

        future_question = VisaDevice(alias="testalias", address="testadress", active=True, connected=True)
        # self.assertIs(future_question.query("testrequest", "testresponse", True).success, True)