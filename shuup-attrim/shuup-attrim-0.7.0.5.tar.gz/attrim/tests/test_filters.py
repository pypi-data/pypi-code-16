from shuup.core.models import Product
from shuup.testing.factories import get_default_shop

from attrim.interface import attrim
from attrim.tests.utils.cases import AttrimTestCase
from attrim.tests.utils.generators import AttrimGenerator
from attrim.types import AttrimType


class FiltersTest(AttrimTestCase):
    @classmethod
    def set_up_class(cls):
        cls.gen = AttrimGenerator()

    def test_trans_str_product_filter(self):
        cls = self.gen.cls.model(type=AttrimType.trans_str, options_amount=3)

        product_0_1 = self.gen.product()
        product_0_1.attrims.create(
            cls_obj=cls,
            options=[
                cls.options[0],
                cls.options[1],
            ],
        )
        product_1_2 = self.gen.product()
        product_1_2.attrims.create(
            cls_obj=cls,
            options=[
                cls.options[1],
                cls.options[2],
            ],
        )

        product_qs_0_1 = attrim.filter_product_qs_by(
            cls=cls,
            option_values_raw=[cls.options[0], cls.options[1]],
            product_qs_source=Product.objects.listed(shop=get_default_shop()),
        )
        self.assert_true(len(product_qs_0_1) >= 2)
        self.assert_true(product_0_1 in product_qs_0_1)
        self.assert_true(product_1_2 in product_qs_0_1)

        product_qs_1_2 = attrim.filter_product_qs_by(
            cls=cls,
            option_values_raw=[cls.options[1], cls.options[2]],
            product_qs_source=Product.objects.listed(shop=get_default_shop()),
        )
        self.assert_true(len(product_qs_1_2) >= 2)
        self.assert_true(product_0_1 in product_qs_1_2)
        self.assert_true(product_1_2 in product_qs_1_2)

        product_qs_1 = attrim.filter_product_qs_by(
            cls=cls,
            option_values_raw=[cls.options[1]],
            product_qs_source=Product.objects.listed(shop=get_default_shop()),
        )
        self.assert_true(len(product_qs_1) >= 2)
        self.assert_true(product_0_1 in product_qs_1)
        self.assert_true(product_1_2 in product_qs_1)
