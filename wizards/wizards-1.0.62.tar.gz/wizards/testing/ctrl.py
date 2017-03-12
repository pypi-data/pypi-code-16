from wizards.testing.base import BaseWSGITestCase


class ControllerTestCase(BaseWSGITestCase):
    controller_class = None

    def setUp(self):
        super(ControllerTestCase, self).setUp()
        self.ctrl = self.controller_class.as_view()
