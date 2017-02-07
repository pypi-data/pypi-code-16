from django.core.urlresolvers import reverse
from shuup_dev_utils.settings import DEFAULT_LANG
from shuup_dev_testutils.cases import ApiAuthTestCase

from attrim.tests import fixtures
from attrim.tests.utils.cases import AttrimTestCase
from attrim.tests.utils.generators import AttrimGenerator


class ClsOptionsTest(AttrimTestCase, ApiAuthTestCase):

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

    def set_up(self):
        # Because ApiAuthTestCase (mixin) `set_up` doesn't called automatically.
        super(AttrimTestCase, self).set_up()

    def test_cls_option_delete(self):
        test_cls = fixtures.create.cls_trans_str(
            code=self.test_cls_code,
            name=self.test_cls_name,
            options=self.test_cls_trans_options,
        )
        edit_url = reverse(
            'shuup_admin:attrim.edit',
            kwargs={'pk': test_cls.pk},
        )
        option_last_index = len(self.test_cls_trans_options) - 1
        option_forms = fixtures.create.option_forms(
            options=self.test_cls_trans_options,
            options_delete=[option_last_index],
        )
        self.client.post(
            path=edit_url,
            data=fixtures.create.formset_post_data(
                cls_name=self.test_cls_name,
                cls_code=test_cls.code,
                cls_type=test_cls.type.value,
                option_forms=option_forms,
            ),
        )
        self.assert_equal(
            test_cls.options,
            self.options_trans_str_default[0:-1],
        )

    def test_cls_option_add(self):
        test_options = self.test_cls_trans_options
        test_cls = fixtures.create.cls_trans_str(
            code=self.test_cls_code,
            name=self.test_cls_name,
            options=test_options,
        )
        option_new_index = len(test_options)
        option_new = self.generator.trans_str_option(order=option_new_index)
        test_options_changed = test_options.copy()
        test_options_changed.append(option_new)
        option_forms = fixtures.create.option_forms(
            options=test_options_changed,
            options_new=[option_new_index],
        )
        edit_url = reverse(
            'shuup_admin:attrim.edit',
            kwargs={'pk': test_cls.pk},
        )
        self.client.post(
            path=edit_url,
            data=fixtures.create.formset_post_data(
                cls_name=self.test_cls_name,
                cls_code=test_cls.code,
                cls_type=test_cls.type.value,
                option_forms=option_forms,
            ),
            follow=True,
        )

        test_options_changed_values = []
        for option in test_options:
            default_value = option['values'][DEFAULT_LANG]
            test_options_changed_values.append(default_value)
        option_new_value = option_new['values'][DEFAULT_LANG]
        test_options_changed_values.append(option_new_value)

        """
        AssertionError:
        ['eum[49 chars]quidem', 'dignissimos', 'voluptas', 'doloremque', 'temporibus'] !=
        ['eum[49 chars]quidem', 'dignissimos', 'voluptas', 'temporibus', 'doloremque']
        """
        # TODO: wrong options order
        self.assert_equal(test_cls.options, test_options_changed_values)

    def test_cls_options_add_and_delete(self):
        test_options = self.test_cls_trans_options
        test_cls = fixtures.create.cls_trans_str(
            code=self.test_cls_code,
            name=self.test_cls_name,
            options=test_options,
        )

        option_new_index = len(test_options)
        option_new = self.generator.trans_str_option(order=option_new_index)
        test_options_extended = test_options.copy()
        test_options_extended.append(option_new)

        test_option_last_index = len(test_options) - 1

        option_forms = fixtures.create.option_forms(
            options=test_options_extended,
            options_new=[option_new_index],
            options_delete=[test_option_last_index],
        )

        edit_url = reverse(
            'shuup_admin:attrim.edit',
            kwargs={'pk': test_cls.pk},
        )
        self.client.post(
            path=edit_url,
            data=fixtures.create.formset_post_data(
                cls_name=self.test_cls_name,
                cls_code=test_cls.code,
                cls_type=test_cls.type.value,
                option_forms=option_forms,
            ),
            follow=True,
        )

        test_options_changed = test_options_extended.copy()
        del test_options_changed[-2]
        test_options_changed_values = []
        for option in test_options_changed:
            default_value = option['values'][DEFAULT_LANG]
            test_options_changed_values.append(default_value)

        self.assert_equal(test_cls.options, test_options_changed_values)
