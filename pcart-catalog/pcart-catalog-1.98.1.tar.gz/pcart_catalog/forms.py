from django import forms
from django.utils.translation import ugettext_lazy as _
from django.forms import BaseInlineFormSet
from .models import Product, ProductVariant


class AddProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'slug', 'product_type', 'status']


class EditProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(EditProductForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:
            obj = kwargs['instance']
            properties_fields = obj.get_properties_fields()
            for p in properties_fields:
                self.fields[p[0]] = p[2]

    def save(self, commit=True):
        instance = super(EditProductForm, self).save(commit=False)
        properties = {}
        properties_fields = instance.get_properties_fields()
        for p in properties_fields:
            _value = self.cleaned_data[p[0]]
            if _value:
                properties[p[1]] = _value
        instance.properties = properties
        if commit:
            instance.save()
        return instance


class EditProductVariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        self.product_instance = kwargs.pop('product_instance')
        super(EditProductVariantForm, self).__init__(*args, **kwargs)
        initial_values = {}
        if 'instance' in kwargs:
            initial_values = kwargs['instance'].properties
        properties_fields = self.product_instance.get_properties_fields(initial_values=initial_values, for_variants=True)
        for p in properties_fields:
            self.fields[p[0]] = p[2]

    def save(self, commit=True):
        instance = super(EditProductVariantForm, self).save(commit=False)
        properties = self.product_instance.properties
        properties_fields = instance.get_properties_fields()
        for p in properties_fields:
            _value = self.cleaned_data[p[0]]
            if _value:
                properties[p[1]] = _value

        instance.properties = properties
        if commit:
            instance.save()
        return instance


class EditProductVariantFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super(EditProductVariantFormSet, self).__init__(*args, **kwargs)
        self.form_kwargs['product_instance'] = kwargs['instance']
