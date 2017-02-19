from __future__ import absolute_import

from celery import shared_task
from django.conf import settings
from twilio.rest import TwilioRestClient

import arrow

from .models import Appointment


# Uses credentials from the TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN
# environment variables
client = TwilioRestClient()

@shared_task
def send_sms_reminder():
    message = client.messages.create(
        body="I Love You!",
        to=settings.phone_number,
        from_=settings.TWILIO_NUMBER,
    )
