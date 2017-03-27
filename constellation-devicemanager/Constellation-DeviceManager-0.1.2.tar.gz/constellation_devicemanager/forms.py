from django.forms import ModelForm

from . import validators

from .models import Device

class DeviceForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(DeviceForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'mdl-textfield__input'
        self.fields['hostname'].widget.attrs['pattern'] = validators.hostname
    class Meta:
        model = Device
        fields = ['MAC', 'name', 'owner', 'hostname']
