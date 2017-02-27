from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponseNotFound
from django.utils.module_loading import import_string


def personal_information(request, template_name='customers/personal_information.html'):
    user = request.user
    context = {
        'user': user,
        'customer_menu': settings.PCART_CUSTOMER_PROFILE_SECTIONS,
    }
    return render(request, template_name, context)


def profile_section(request, slug):
    for section in settings.PCART_CUSTOMER_PROFILE_SECTIONS:
        if slug == section['slug']:
            view = import_string(section['view'])
            kwargs = section.get('kwargs', dict())
            return view(request, **kwargs)
    return HttpResponseNotFound('Unknown profile section')


def customer_toolbar(request, template_name='customers/includes/_customer_toolbar_content.html'):
    user = request.user
    context = {
        'user': user,
    }
    return render(request, template_name, context)
