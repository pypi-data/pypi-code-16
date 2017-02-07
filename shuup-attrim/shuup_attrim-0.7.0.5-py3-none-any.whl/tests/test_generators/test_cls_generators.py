from shuup_dev_testutils.cases import SnakeTestCase

from attrim.tests.utils.generators.cls import ClsGenerator
from attrim.types import AttrimType


class ClsGeneratorTest(SnakeTestCase):
    cls_gen = None

    def set_up(self):
        self.cls_gen = ClsGenerator()

    def test_cls_options_amount(self):
        amount_expected = 5
        cls = self.cls_gen.model(type=AttrimType.int, options_amount=amount_expected)
        amount_actual = len(cls.options)
        self.assert_equal(amount_expected, amount_actual)

    # noinspection PyBroadException
    def test_cls_options_list(self):
        try:
            self.cls_gen.options.list()
        except:
            self.fail('can not generate default options list')
