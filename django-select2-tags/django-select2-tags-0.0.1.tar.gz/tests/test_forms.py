import unittest

from select2_tags import forms
from tests import forms as test_forms, models as test_models


class TestSelect2ModelChoiceField(unittest.TestCase):

    def setUp(self):
        self.related1 = test_models.MyRelatedModel.objects.create(name='item1')
        self.field = forms.Select2ModelChoiceField(
            'my_m2m_field', queryset=test_models.MyRelatedModel.objects.all())

    def test_to_python_no_values(self):
        value = None

        python_value = self.field.to_python(value)

        self.assertIsNone(python_value)
        self.assertEqual(set(), self.field.new_items)

    def test_to_python_new_value(self):
        value = 'new1'

        python_value = self.field.to_python(value)

        self.assertIsNone(python_value)
        self.assertEqual({'new1'}, self.field.new_items)

    def test_to_python_existing_value(self):
        value = str(self.related1.pk)

        python_value = self.field.to_python(value)

        self.assertEqual(self.related1, python_value)
        self.assertEqual(set(), self.field.new_items)


class TestSelect2ModelMultipleChoiceField(unittest.TestCase):

    def setUp(self):
        self.related1 = test_models.MyRelatedModel.objects.create(name='item1')
        self.related2 = test_models.MyRelatedModel.objects.create(name='item2')
        self.field = forms.Select2ModelMultipleChoiceField(
            'name', queryset=test_models.MyRelatedModel.objects.all())

    def test__check_values_no_values(self):
        values = []

        checked_values = self.field._check_values(values)

        self.assertEqual(0, checked_values.count())
        self.assertEqual(set(), self.field.new_items)

    def test__check_values_new_only(self):
        values = ['new1', 'new2']

        checked_values = self.field._check_values(values)

        self.assertEqual(0, checked_values.count())
        self.assertEqual({'new1', 'new2'}, self.field.new_items)

    def test__check_values_existing_only(self):
        values = [str(self.related1.pk), str(self.related2.pk)]

        checked_values = self.field._check_values(values)

        self.assertEqual(2, checked_values.count())
        self.assertEqual(self.related1, checked_values[0])
        self.assertEqual(self.related2, checked_values[1])
        self.assertEqual(set(), self.field.new_items)

    def test__check_values_new_and_existing(self):
        values = [str(self.related1.pk), str(self.related2.pk), 'new1', 'new2']

        checked_values = self.field._check_values(values)

        self.assertEqual(2, checked_values.count())
        self.assertEqual(self.related1, checked_values[0])
        self.assertEqual(self.related2, checked_values[1])
        self.assertEqual({'new1', 'new2'}, self.field.new_items)

    def test_save_new_values_save_disabled(self):
        self.field.save_new = False
        num_existing_items = test_models.MyRelatedModel.objects.filter(name__contains='new').count()

        try:
            self.field.save_new_values()
            self.fail("Should not be able to save when save_new is False")
        except ValueError as e:
            expected = 'Should not call save_new_values when save_new is False'
            self.assertEqual(expected, str(e))

        items = test_models.MyRelatedModel.objects.filter(name__contains='new')
        self.assertEqual(num_existing_items, items.count())

    def test_save_new_values_no_values(self):
        num_existing_items = test_models.MyRelatedModel.objects.filter(name__contains='new').count()

        created_items = self.field.save_new_values()

        # Verify that no new items are returned
        self.assertEqual(0, created_items.count())
        # Verify that no new items are in db
        items = test_models.MyRelatedModel.objects.filter(name__contains='new')
        self.assertEqual(num_existing_items, items.count())

    def test_save_new_values(self):
        self.field.new_items = ['new1', 'new2']
        num_existing_items = test_models.MyRelatedModel.objects.filter(name__contains='new').count()

        created_items = self.field.save_new_values()

        # Verify that new items are returned
        self.assertEqual(2, created_items.count())
        self.assertEqual('new1', created_items[0].name)
        self.assertEqual('new2', created_items[1].name)
        # Verify that new items are in db
        items = test_models.MyRelatedModel.objects.filter(name__contains='new')
        self.assertEqual(num_existing_items + 2, items.count())


class TestSelect2ModelFormFk(unittest.TestCase):

    def setUp(self):
        self.related1 = test_models.MyRelatedModel.objects.create(name='item1')

    def test_save_new_only(self):
        self.form = test_forms.MyFkForm(data={'my_fk_field': 'new1'})
        self.form.is_valid()

        instance = self.form.save()

        self.assertIsNotNone(instance.pk)
        self.assertEqual('new1', instance.my_fk_field.name)

    def test_save_existing_only(self):
        self.form = test_forms.MyFkForm(data={'my_fk_field': str(self.related1.pk)})
        self.form.is_valid()

        instance = self.form.save()

        self.assertIsNotNone(instance.pk)
        self.assertEqual(self.related1, instance.my_fk_field)


class TestSelect2ModelFormM2m(unittest.TestCase):

    def setUp(self):
        self.related1 = test_models.MyRelatedModel.objects.create(name='item1')
        self.related2 = test_models.MyRelatedModel.objects.create(name='item2')

    def test_save_no_data(self):
        self.form = test_forms.MyM2mForm(data={})
        self.form.is_valid()

        instance = self.form.save()

        self.assertIsNotNone(instance.pk)

    def test_save_new_only(self):
        self.form = test_forms.MyM2mForm(data={'my_m2m_field': ['new1', 'new2']})
        self.form.is_valid()

        instance = self.form.save()

        self.assertIsNotNone(instance.pk)
        self.assertEqual(2, instance.my_m2m_field.count())
        self.assertEqual('new1', instance.my_m2m_field.all()[0].name)
        self.assertEqual('new2', instance.my_m2m_field.all()[1].name)

    def test_save_existing_only(self):
        pks = [str(self.related1.pk), str(self.related2.pk)]
        self.form = test_forms.MyM2mForm(data={'my_m2m_field': pks})
        self.form.is_valid()

        instance = self.form.save()

        self.assertIsNotNone(instance.pk)
        self.assertEqual(2, instance.my_m2m_field.count())
        self.assertEqual(self.related1, instance.my_m2m_field.all()[0])
        self.assertEqual(self.related2, instance.my_m2m_field.all()[1])

    def test_save_new_and_existing(self):
        pks = [str(self.related1.pk), str(self.related2.pk), 'new1', 'new2']
        self.form = test_forms.MyM2mForm(data={'my_m2m_field': pks})
        self.form.is_valid()

        instance = self.form.save()

        self.assertIsNotNone(instance.pk)
        self.assertEqual(4, instance.my_m2m_field.count())
        self.assertEqual(self.related1, instance.my_m2m_field.all()[0])
        self.assertEqual(self.related2, instance.my_m2m_field.all()[1])
        self.assertEqual('new1', instance.my_m2m_field.all()[2].name)
        self.assertEqual('new2', instance.my_m2m_field.all()[3].name)
