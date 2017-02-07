from attrim.types import AttrimType
from attrim.tests.utils.cases import AttrimTestCase


class AttributeIntTest(AttrimTestCase):

    def test_create(self):
        cls = self.gen.cls.model(type=AttrimType.int, options_amount=5)
        self.product.attrims.create(
            cls_code=cls.code,
            options=[cls.options[0], cls.options[1]],
        )
        attr = self.product.attrims.get(code=cls.code)
        options_expected = [cls.options[0], cls.options[1]]
        self.assert_equal(options_expected, attr.options)

    def test_options_overwrite(self):
        cls = self.gen.cls.model(type=AttrimType.int, options_amount=5)
        self.product.attrims.create(
            cls_code=cls.code,
            options=[cls.options[0], cls.options[1]],
        )
        attr = self.product.attrims.get(code=cls.code)
        options_new = [cls.options[2], cls.options[3]]
        attr.options = options_new
        self.assert_equal(expected=options_new, actual=attr.options)
