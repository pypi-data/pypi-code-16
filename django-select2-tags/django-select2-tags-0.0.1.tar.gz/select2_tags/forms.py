from django import forms


class Select2Mixin(object):
    """ Handle creation of new values in (multiple) choice fields in the UI """

    def __init__(self, value_field, save_new=True, *args, **kwargs):
        """value_field is the field name in the model to be populated by new values entered in UI"""
        super(Select2Mixin, self).__init__(*args, **kwargs)
        self.value_field = value_field
        self.save_new = save_new
        self.new_items = set()

    def separate_new_values(self, values):
        self.new_items = set()
        key = self.to_field_name or 'pk'
        pk_values = []
        for pk in values:
            try:
                self.queryset.filter(**{key: pk})
                pk_values.append(pk)
            except (ValueError, TypeError):
                if pk:
                    self.new_items.add(pk)
        return pk_values

    def save_new_values(self):
        """
        Save any new values (tags) entered in the select2 box
        """
        if not self.save_new:
            raise ValueError('Should not call save_new_values when save_new is False')
        created_ids = []
        for item in self.new_items:
            create_kwargs = {self.value_field: item}
            new_object = self.queryset.model.objects.create(**create_kwargs)
            created_ids.append(new_object.pk)
        created_items = self.queryset.model.objects.filter(pk__in=created_ids)
        return created_items


class Select2ModelChoiceField(Select2Mixin, forms.ModelChoiceField):
    """ Handle creation of a new value in a choice field in the UI """

    def to_python(self, value):
        pk_values = self.separate_new_values([value])
        if pk_values:
            return super(Select2ModelChoiceField, self).to_python(value)
        return None


class Select2ModelMultipleChoiceField(Select2Mixin, forms.ModelMultipleChoiceField):
    """ Handle creation of new values in a multiple choice field in the UI """

    def _check_values(self, value):
        """
        Before calling super _check_values, set aside any values for new objects to be created
        """
        pk_values = self.separate_new_values(value)
        return super(Select2ModelMultipleChoiceField, self)._check_values(pk_values)


class Select2ModelForm(forms.ModelForm):

    def save(self, *args, **kwargs):
        instance = super(Select2ModelForm, self).save(*args, **kwargs)
        dirty = False
        for field_name in self.fields:
            field = self.fields[field_name]
            if isinstance(field, Select2Mixin):
                if field.save_new:
                    new_values = field.save_new_values()
                    if new_values:
                        model_field = getattr(instance, field_name)
                        if isinstance(field, Select2ModelMultipleChoiceField):
                            model_field.add(*new_values)
                        else:
                            setattr(instance, field_name, new_values[0])
                            dirty = True
        if dirty:
            instance.save()
        return instance


# TODO put tags back in select2 field after form fails validation?
# TODO test that required fields work correctly
