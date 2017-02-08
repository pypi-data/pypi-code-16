from unittest import TestCase
from .users import UserProfile, UserProfileBatch


class TestUserProfile(TestCase):
    def test_required_attrs(self):
        try:
            profile = UserProfile()
            self.fail("Should have raised an assertion error")
        except AssertionError:
            pass

    def test_required_attrs_provided(self):
        try:
            profile = UserProfile(EmpId='hello', FeedRecordNumber='Number',
                                  LoginId='newLoginID', Password='test')
        except:
            self.fail("Should not have raised an error")

    def test_to_xml(self):
        profile = UserProfile(EmpId='hello', FeedRecordNumber='Number',
                              LoginId='newLoginID', Password='test')
        profile_xml = profile.to_xml()
        self.assertIsNotNone(profile_xml)
        for field in profile.REQUIRED_FIELDS:
            self.assertIn(field, profile_xml)


class TestUserProfileBatch(TestCase):
    def test_all_profiles(self):
        profiles = [UserProfile(EmpId='hello', FeedRecordNumber='Number',
                              LoginId='newLoginID', Password='test')]
        user_profile_batch = UserProfileBatch(profiles)
        xml_result = user_profile_batch.to_xml()
        self.assertIsNotNone(xml_result)


