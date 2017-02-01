from .models import ScheduledEmail, UserProfile
from django.core import mail
from proso.django.test import TestCase
from django.contrib.auth.models import User


class ScheduledEmailTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='test', email='test@localhost.com', password='top_secret')
        self.profile = UserProfile.objects.get(user=self.user)

    def test_send_scheduled_email(self):
        ScheduledEmail.objects.schedule(
            self.user, 'test subject', 'test message', 'from@localhost.com'
        )
        self.assertEqual(ScheduledEmail.objects.get(subject='test subject').status, ScheduledEmail.STATUS_SCHEDULED)
        ScheduledEmail.objects.send()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'test subject')
        self.assertEqual(ScheduledEmail.objects.get(subject='test subject').status, ScheduledEmail.STATUS_SENT)
        self.profile.send_emails = False
        self.profile.save()
        ScheduledEmail.objects.schedule(
            self.user, 'test 2 subject', 'test message', 'from@localhost.com'
        )
        self.assertEqual(ScheduledEmail.objects.get(subject='test 2 subject').status, ScheduledEmail.STATUS_SCHEDULED)
        ScheduledEmail.objects.send()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(ScheduledEmail.objects.get(subject='test 2 subject').status, ScheduledEmail.STATUS_SKIPPED)
