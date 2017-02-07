from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from shuup_dev_utils.settings import DEFAULT_LANG
from shuup_dev_testutils.cases import ApiAuthTestCase

from attrim.interface import attrim
from attrim.tests import fixtures
from attrim.tests.utils.cases import AttrimTestCase
from attrim.tests.utils.generators import AttrimGenerator
from attrim.types import AttrimType


class ClsTest(AttrimTestCase, ApiAuthTestCase):
    cls_create_url = None

    @classmethod
    def set_up_class(cls):
        super().set_up_class()

        cls.gen = AttrimGenerator()

        cls.generator = fixtures.generators.Generator()
        cls.test_cls_code = cls.generator.code()
        cls.test_cls_name = cls.generator.name()
        cls.test_cls_trans_options = cls.generator.trans_str_options()

        cls.options_trans_str_default = []
        for option_index, option in enumerate(cls.test_cls_trans_options):
            option = cls.test_cls_trans_options[option_index]
            default_lang_value = option['values'][DEFAULT_LANG]
            cls.options_trans_str_default.append(default_lang_value)
        
        cls.cls_create_url = reverse('shuup_admin:attrim.new')

    def set_up(self):
        # Because ApiAuthTestCase (mixin) `set_up` doesn't called automatically.
        super(AttrimTestCase, self).set_up()

    def test_create_cls_of_int_type(self):
        cls_code = self.gen.cls.code()

        self.client.post(
            path=self.cls_create_url,
            data=fixtures.create.formset_post_data(
                cls_name=self.gen.cls.name(),
                cls_code=cls_code,
                cls_type=AttrimType.int.value,
                option_forms=[
                    dict(order=4, is_new=True, value='1'),
                    dict(order=1, is_new=True, value='4'),
                    dict(order=3, is_new=True, value='2'),
                    dict(order=2, is_new=True, value='3'),
                ],
            ),
        )

        cls_created = attrim.cls.get(code=cls_code)
        self.assert_equal([4, 3, 2, 1], cls_created.options)

    def test_create_cls_of_float_type(self):
        cls_code = self.gen.cls.code()

        self.client.post(
            path=self.cls_create_url,
            data=fixtures.create.formset_post_data(
                cls_name=self.gen.cls.name(),
                cls_code=cls_code,
                cls_type=AttrimType.float.value,
                option_forms=[
                    dict(order=4, is_new=True, value='4.4115'),
                    dict(order=1, is_new=True, value='1.3114'),
                    dict(order=3, is_new=True, value='3.1888'),
                    dict(order=2, is_new=True, value='2.0991'),
                ],
            ),
        )

        cls_created = attrim.cls.get(code=cls_code)
        self.assert_equal([1.3114, 2.0991, 3.1888, 4.4115], cls_created.options)

    def test_create_cls_of_str_type(self):
        cls_code = self.gen.cls.code()

        self.client.post(
            path=self.cls_create_url,
            data=fixtures.create.formset_post_data(
                cls_name=self.gen.cls.name(),
                cls_code=cls_code,
                cls_type=AttrimType.str.value,
                option_forms=[
                    dict(order=4, is_new=True, value='text four'),
                    dict(order=1, is_new=True, value='text one'),
                    dict(order=3, is_new=True, value='text three'),
                    dict(order=2, is_new=True, value='text two'),
                ],
            ),
        )

        cls_created = attrim.cls.get(code=cls_code)
        self.assert_equal(
            ['text one', 'text two', 'text three', 'text four'],
            cls_created.options,
        )

    def test_create_cls_of_trans_str_type(self):
        trans_options = self.test_cls_trans_options
        option_forms = fixtures.create.option_forms(
            options=self.test_cls_trans_options,
            # all of the options are new
            options_new=[index for index, option in enumerate(trans_options)],
        )

        self.client.post(
            path=self.cls_create_url,
            data=fixtures.create.formset_post_data(
                cls_name=self.test_cls_name,
                cls_code=self.test_cls_code,
                cls_type=attrim.AttrimType.trans_str.value,
                option_forms=option_forms,
            ),
        )
        # test post result
        test_cls = attrim.cls.get(code=self.test_cls_code)
        self.assert_equal(test_cls.code, self.test_cls_code)
        self.assert_equal(
            test_cls.options,
            self.options_trans_str_default,
        )
        response = self.client.get(
            path=reverse(
                'shuup_admin:attrim.edit',
                kwargs={'pk': test_cls.pk}
            ),
        )
        for option_default_value in self.options_trans_str_default:
            self.assert_contains(response, option_default_value)

    def test_cls_delete(self):
        test_cls = attrim.cls.create(
            name=self.test_cls_name,
            code=self.test_cls_code,
            type=attrim.AttrimType.trans_str,
        )
        test_cls.options = self.test_cls_trans_options

        self.client.post(
            path=reverse(
                'shuup_admin:attrim.delete',
                kwargs={'pk': test_cls.pk},
            )
        )

        with self.assert_raises(ObjectDoesNotExist):
            attrim.cls.get(code=self.test_cls_code)
