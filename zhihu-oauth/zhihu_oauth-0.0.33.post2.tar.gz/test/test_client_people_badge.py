from .client_test_base import ZhihuClientClassTest


class TestPeopleBadgeNumber(ZhihuClientClassTest):
    def test_badge_topics_number(self):
        self.assertEqual(len(list(self.client.people("giantchen").badge.topics)), 3)

    def test_people_has_badge(self):
        self.assertTrue(self.client.people("giantchen").badge.has_badge)

    def test_people_has_indentity(self):
        self.assertFalse(self.client.people("giantchen").badge.has_identity)

    def test_people_is_best_answerer_or_not(self):
        self.assertTrue(self.client.people("giantchen").badge.is_best_answerer)

    def test_people_identify_information(self):
        self.assertIsNone(self.client.people("giantchen").badge.identity)
