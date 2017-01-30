"""
Unittests for Patients
"""
from mock import patch
from opal.core.test import OpalTestCase

from opal.models import Patient, Episode
from opal.tests.models import InvisibleDog


class PatientTest(OpalTestCase):

    def setUp(self):
        self.patient = Patient.objects.create()

    def test_singleton_subrecord_created(self):
        self.assertEqual(1, self.patient.famouslastwords_set.count())

    def test_can_create_episode(self):
        episode = self.patient.create_episode()
        self.assertEqual(Episode, type(episode))

    def test_get_active_episode(self):
        self.patient.create_episode()
        episode2 = self.patient.create_episode()
        episode2.set_tag_names(['microbiology'], None)
        self.assertEqual(episode2.id, self.patient.get_active_episode().id)

    def test_get_active_episode_with_no_episodes(self):
        self.assertIsNone(self.patient.get_active_episode())

    def test_get_active_episode_with_no_active_episodes(self):
        self.patient.create_episode()
        self.patient.create_episode()
        self.assertIsNone(self.patient.get_active_episode())

    @patch('opal.models.patient_subrecords')
    @patch('opal.models.episode_subrecords')
    def test_not_bulk_serialisable_patient_subrecords(
        self, episode_subrecords, patient_subrecords
    ):
        episode_subrecords.return_value = []
        patient_subrecords.return_value = [InvisibleDog]
        patient, episode = self.new_patient_and_episode_please()
        InvisibleDog.objects.create(patient=patient)
        to_dict = patient.to_dict(self.user)
        self.assertNotIn(InvisibleDog.get_api_name(), to_dict)
        self.assertNotIn(InvisibleDog.get_api_name(), to_dict['episodes'][1])
