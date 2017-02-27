from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import login, logout

from .forms import LoginForm
from .models import GlobalTemplateSettings, SidebarLink, TitlebarLink

def login_view(request):
    template_settings_object = GlobalTemplateSettings(allowBackground=True)
    template_settings = template_settings_object.settings_dict()
    form = LoginForm(request.POST or None)
    if request.POST and form.is_valid():
        user = form.login(request)
        if user:
            login(request, user)
            return HttpResponseRedirect("/")
    return render(request, 'SimpleBase/login.html', {
        'form': form,
        'template_settings': template_settings,
    })
