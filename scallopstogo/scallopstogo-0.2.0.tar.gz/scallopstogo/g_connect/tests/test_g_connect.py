from unittest import TestCase
from ...g_connect import get_google_service

class TestGConnect(TestCase):
    '''
    Test google api connections
    '''

    def test_is_gservice(self):
        '''
        check function returns not None
        '''

        with open('/Users/andrewlee/Google Drive/ishbooks/calendar_automation/bi_onboarding/storage.json') as data_file:
            storage = data_file.read()

        service = get_google_service(storage, 'calendar', 'v3')

        self.assertIsNotNone(service)

        