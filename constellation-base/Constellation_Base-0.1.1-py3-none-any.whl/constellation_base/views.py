from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import login, logout
from django.conf import settings
from django.utils.module_loading import import_module
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from .forms import LoginForm
from .models import GlobalTemplateSettings, SidebarLink, TitlebarLink

@login_required
def index_view(request):
    template_settings_object = GlobalTemplateSettings(allowBackground=True)
    template_settings = template_settings_object.settings_dict()
    constellation_apps = []
    for appname in settings.INSTALLED_APPS:
        if not "django" in appname:
            app = import_module(appname)
            if hasattr(app.views, 'view_dashboard'):
                constellation_apps.append({'name': appname,
                                           'url': reverse(app.views.view_dashboard)})

    return render(request, 'constellation_base/index.html', {
        'template_settings': template_settings,
        'apps': constellation_apps,
    })

def login_view(request):
    template_settings_object = GlobalTemplateSettings(allowBackground=True)
    template_settings = template_settings_object.settings_dict()
    form = LoginForm(request.POST or None)
    if "next" in request.GET:
        next_page = request.GET["next"]
    else:
        next_page = "/"
    if request.POST and form.is_valid():
        user = form.login(request)
        if user:
            login(request, user)
            if request.POST["next"]:
                return HttpResponseRedirect(request.POST["next"])
            else:
                return HttpResponseRedirect("/")
    return render(request, 'constellation_base/login.html', {
        'form': form,
        'template_settings': template_settings,
        'next': next_page,
    })

def logout_view(request):
    logout(request)
    return redirect("Login")
