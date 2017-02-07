from parler.utils.context import switch_language
from shuup_dev_utils.settings import DEFAULT_LANG, LANG_LIST

from attrim.tests.utils.cases import AttrimTestCase
from attrim.types import AttrimType


class AttributesTransStrTest(AttrimTestCase):

    def test_create(self):
        cls = self.gen.cls.model(AttrimType.trans_str)
        attr = self.product.attrims.create(
            cls_code=cls.code,
            options=[cls.options[0], cls.options[1]],
        )
        try:
            self.product.attrims.get(code=cls.code)
        except attr.DoesNotExist:
            self.fail('Could not request created attribute by code.')

    def test_options_order(self):
        cls = self.gen.cls.model(AttrimType.trans_str)
        attr = self.product.attrims.create(
            cls_code=cls.code,
            options=[cls.options[0], cls.options[1]],
        )
        self.assert_equal(
            expected=[cls.options[0], cls.options[1]],
            actual=attr.options,
        )

    def test_name_translations(self):
        cls_name_initial = self.gen.cls.name()
        cls = self.gen.cls.model(name=cls_name_initial)
        attr = self.product.attrims.create(
            cls_code=cls.code,
            options=[cls.options[0], cls.options[1]],
        )
        for lang_code in LANG_LIST:
            with switch_language(attr.cls, lang_code):
                self.assert_equal(
                    cls_name_initial[lang_code],
                    attr.cls.name,
                )

    def test_options_translations_values(self):
        cls_options_initial = self.gen.cls.options.list(type=AttrimType.trans_str)
        cls = self.gen.cls.model(options=cls_options_initial)
        attr = self.product.attrims.create(
            cls_code=cls.code,
            options=[cls.options[0], cls.options[1]],
        )
        for lang_code in LANG_LIST:
            with switch_language(attr.cls, lang_code):
                self.assert_equal(
                    cls_options_initial[0]['values'][lang_code],
                    attr.options[0],
                )
                self.assert_equal(
                    cls_options_initial[1]['values'][lang_code],
                    attr.options[1],
                )

    def test_options_overwrite(self):
        cls_options_initial = self.gen.cls.options.list(
            type=AttrimType.trans_str,
            amount=4,
        )
        cls = self.gen.cls.model(options=cls_options_initial)
        attr = self.product.attrims.create(
            cls_code=cls.code,
            options=[cls.options[0], cls.options[1]],
        )

        attr.options = [cls.options[2], cls.options[3]]

        self.assert_equal(
            expected=[
                cls_options_initial[2]['values'][DEFAULT_LANG],
                cls_options_initial[3]['values'][DEFAULT_LANG],
            ],
            actual=attr.options,
        )
        for lang_code in LANG_LIST:
            with switch_language(attr.cls, lang_code):
                self.assert_equal(
                    expected=cls_options_initial[2]['values'][lang_code],
                    actual=attr.options[0],
                )
                self.assert_equal(
                    expected=cls_options_initial[3]['values'][lang_code],
                    actual=attr.options[1],
                )

    def test_delete(self):
        cls = self.gen.cls.model(AttrimType.trans_str)
        self.product.attrims.create(
            cls_code=cls.code,
            options=[cls.options[0], cls.options[1]],
        )
        self.product.attrims.delete(code=cls.code)

        product_attrs_num = len(self.product.attrims.all())
        self.assert_equal(expected=0, actual=product_attrs_num)
