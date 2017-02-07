from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.utils import IntegrityError
from parler.utils.context import switch_language
from shuup_dev_utils.settings import LANG_LIST
from shuup_dev_utils.settings import DEFAULT_LANG

from attrim.interface import attrim
from attrim.types import AttrimType
from attrim.tests.utils.cases import AttrimTestCase


class ClsTransStrTest(AttrimTestCase):

    def test_cls_creation_names(self):
        cls_name_dict = self.gen.cls.name()
        cls = self.gen.cls.model(name=cls_name_dict, type=AttrimType.trans_str)

        for lang_code in LANG_LIST:
            with switch_language(cls, lang_code):
                cls_expected_name = cls_name_dict[lang_code]
                self.assert_equal(cls.name, cls_expected_name)

    def test_cls_creation_options(self):
        cls_options_orig = self.gen.cls.options.list(type=AttrimType.trans_str, amount=5)
        cls = self.gen.cls.model(type=AttrimType.trans_str, options=cls_options_orig)

        for option_orig in cls_options_orig:
            option_orig_value = option_orig['values'][DEFAULT_LANG]
            try:
                cls.options.get_option_by_value(option_orig_value)
            except ValueError:
                self.fail('cls option creation failed')

    def test_cls_creation_code_duplicate_error(self):
        cls = self.gen.cls.model()
        with transaction.atomic():
            with self.assert_raises(IntegrityError):
                attrim.cls.create(
                    code=cls.code,
                    type=attrim.AttrimType.trans_str,
                    name=cls.name,
                )

    def test_cls_delete(self):
        cls_code = self.gen.cls.code()
        self.gen.cls.model(code=cls_code)

        attrim.cls.delete(code=cls_code)

        with self.assert_raises(ObjectDoesNotExist):
            attrim.cls.get(code=cls_code)

    def test_options_remove_from_cls_removes_it_on_attr(self):
        options_initial = self.gen.cls.options.list(amount=5)
        cls = self.gen.cls.model(options=options_initial)

        self.product.attrims.create(
            cls_code=cls.code,
            options=[cls.options[0], cls.options[1]],
        )
        attr = self.product.attrims.get(code=cls.code)

        cls.options.remove(cls.options[1])
        self.assert_equal(
            [
                options_initial[0]['values'][DEFAULT_LANG],

                options_initial[2]['values'][DEFAULT_LANG],
                options_initial[3]['values'][DEFAULT_LANG],
                options_initial[4]['values'][DEFAULT_LANG],
            ],
            cls.options,
        )

        attr_options_after_delete = [options_initial[0]['values'][DEFAULT_LANG]]
        self.assert_equal(
            expected=attr_options_after_delete,
            actual=attr.options,
            fail_message="removing of the option from the cls did not affected "
                         "it's attribute",
        )

        with self.assert_raises(ObjectDoesNotExist):
            cls.options.remove(options_initial[1]['values'][DEFAULT_LANG])

    def test_add_options_to_cls_with_order(self):
        self._test_add_options_to_cls(is_with_order=True)

    def test_add_options_to_cls_without_order(self):
        self._test_add_options_to_cls(is_with_order=False)

    def _test_add_options_to_cls(self, is_with_order: bool):
        cls = self.gen.cls.model(options_amount=2)

        options_values_initial = cls.options.copy()

        if is_with_order:
            order_highest = len(cls.options)
            order = order_highest + 1
        else:
            order = None
        option_new = self.gen.cls.options._trans_str(order=order)

        cls.options.add(options=[option_new,])

        option_new_value = option_new['values'][DEFAULT_LANG]
        options_expected = options_values_initial + [option_new_value]

        self.assert_equal(options_expected, cls.options)
