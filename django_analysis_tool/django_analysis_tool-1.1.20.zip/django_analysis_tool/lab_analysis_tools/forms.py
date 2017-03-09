# In forms.py...
from django import forms

class DocumentForm(forms.Form):
    docfile = forms.FileField(label='Select a zip file to upload,if upload or unzip failed, please select valid zip file',)


class JsonForm(forms.Form):
    docfile = forms.FileField(label='Select a json file to upload. If not ,It will use default json file',)


