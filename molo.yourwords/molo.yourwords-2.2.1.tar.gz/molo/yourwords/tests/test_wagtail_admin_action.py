import datetime

from molo.core.models import SiteLanguage
from molo.core.tests.base import MoloTestCaseMixin

from molo.yourwords.models import (YourWordsCompetition,
                                   YourWordsCompetitionEntry,
                                   YourWordsCompetitionIndexPage)

from django.test import TestCase, RequestFactory
from django.test.client import Client


class TestAdminActions(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = self.login()
        self.mk_main()
        # Creates Main language
        self.english = SiteLanguage.objects.create(locale='en')
        # Create competition index page
        self.competition_index = YourWordsCompetitionIndexPage(
            title='Your words competition', slug='Your-words-competition')
        self.main.add_child(instance=self.competition_index)
        self.competition_index.save_revision().publish()

    def test_export_csv(self):
        comp = YourWordsCompetition(
            title='Test Competition',
            description='This is the description')
        self.competition_index.add_child(instance=comp)
        comp.save_revision().publish()

        YourWordsCompetitionEntry.objects.create(
            competition=comp,
            user=self.user,
            story_name='test',
            story_text='test body',
            terms_or_conditions_approved=True,
            hide_real_name=True
        )
        client = Client()
        client.login(username='superuser', password='pass')

        response = self.client.post('/admin/yourwords/'
                                    'yourwordscompetitionentry/')

        date = str(datetime.datetime.now().date())

        expected_output = (
            'competition,submission_date,user,story_name,story_text,'
            'terms_or_conditions_approved,hide_real_name,is_read,'
            'is_shortlisted,is_winner\r\n'
            '7,{0},1,test,test body,1,1,0,0,0'.format(date)
        )

        self.assertContains(response, expected_output)
