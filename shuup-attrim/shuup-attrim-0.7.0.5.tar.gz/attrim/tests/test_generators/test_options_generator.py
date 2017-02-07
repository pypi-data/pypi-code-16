from shuup_dev_testutils.cases import SnakeTestCase

from attrim.tests.utils.generators.options import OptionsGenerator


class OptionsGeneratorTest(SnakeTestCase):
    gen = None

    def set_up(self):
        self.gen = OptionsGenerator()

    def test_int_list_length(self):
        options_amount_expected = 5
        options_generated = self.gen.list(amount=options_amount_expected)
        options_amount_actual = len(options_generated)
        self.assert_equal(options_amount_expected, options_amount_actual)

    def test_int_list_order(self):
        options_amount = 5
        options_generated = self.gen.list(amount=options_amount)
        for option_index in range(0, options_amount):
            option_order_actual = options_generated[option_index]['order']
            option_order_expected= option_index
            self.assert_equal(option_order_expected, option_order_actual)
