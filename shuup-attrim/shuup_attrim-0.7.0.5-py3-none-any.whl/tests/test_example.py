from parler.utils.context import switch_language
from shuup.testing.factories import create_product
from shuup.testing.factories import get_default_product_type

from attrim.interface import attrim
from attrim.tests.utils.cases import AttrimTestCase
from attrim.tests.utils.decorators import require_enabled_languages


class ExampleTest(AttrimTestCase):
    @require_enabled_languages('en', 'fi')
    def test_api_example(self):
        game = get_default_product_type()

        product = create_product(
            sku='WITCHER3',
            name='The Witcher 3: Wild Hunt',
            type=game,
        )
        cls = attrim.cls.create(
            code='localization',
            name=dict(en='Localization', fi='Lokalisointi'),
            type=attrim.AttrimType.trans_str,
            product_type=game,
            options=[
                {'order': 1, 'values': dict(en='english', fi='englanti')},
                {'order': 2, 'values': dict(en='polish',  fi='puola')},
                {'order': 3, 'values': dict(en='german',  fi='saksa')},
                {'order': 4, 'values': dict(en='italian', fi='italialainen')},
                {'order': 5, 'values': dict(en='french',  fi='ranskalainen')},
            ],
        )
        attribute = product.attrims.create(
            cls_obj=cls,
            options=['englanti', 'puola', 'ranskalainen'],
        )

        # check render in different locales
        with switch_language(attribute.cls, 'en'):
            self.assert_equal(attribute.name, 'Localization')
            self.assert_equal(attribute.options, ['english', 'polish', 'french'])
        with switch_language(attribute.cls, 'fi'):
            self.assert_equal(attribute.name, 'Lokalisointi')
            self.assert_equal(
                attribute.options,
                ['englanti', 'puola', 'ranskalainen']
            )

        # delete an option from class, thus delete it from all attributes of
        # the class
        cls.options.remove(option='french')
        self.assert_equal(
            cls.options,
            ['english', 'polish', 'german', 'italian']
        )
        self.assert_equal(
            attribute.options,
            ['english', 'polish']
        )

        # add option to class
        cls.options.add(option={
            'order': 5,
            'values': dict(en='finnish', fi='suomalainen'),
        })
        self.assert_equal(
            cls.options,
            ['english', 'polish', 'german', 'italian', 'finnish']
        )

        # rewrite options of product attribute
        attribute.options = ['english', 'polish', 'finnish']
        self.assert_equal(attribute.options, ['english', 'polish', 'finnish'])
