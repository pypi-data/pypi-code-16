from django.forms import ModelForm

from .models import Device

class DeviceForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(DeviceForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'mdl-textfield__input'
    class Meta:
        model = Device
        fields = ['MAC', 'name', 'owner']
