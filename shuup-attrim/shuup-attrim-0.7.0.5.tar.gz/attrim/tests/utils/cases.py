from shuup_dev_testutils.cases import SnakeTestCase

from attrim.tests.utils.generators import AttrimGenerator


class AttrimTestCase(SnakeTestCase):
    gen = None
    product = None

    @classmethod
    def set_up_class(cls):
        super().set_up_class()
        gen = AttrimGenerator()
        cls.product = gen.product()

    def set_up(self):
        # AttrimGenerator can't generate more than few hundreds unique words,
        # so should be reseted after every test.
        self.gen = AttrimGenerator()
