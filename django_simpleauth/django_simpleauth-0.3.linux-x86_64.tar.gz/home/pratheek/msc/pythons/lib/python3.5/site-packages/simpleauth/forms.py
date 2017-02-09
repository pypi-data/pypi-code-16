from django import forms

from .models import Users

class StartForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = Users
        # fields = ('username', 'password')
        fields = ('username', 'password')
        # widgets = {
        #     'username' : forms.CharField(),
        #     'password' : forms.PasswordInput(),
        # }
        # fields = '__all__'
