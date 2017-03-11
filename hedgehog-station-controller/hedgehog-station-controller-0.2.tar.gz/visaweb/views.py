from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views import generic
from .models import VisaDevice, VisaEvent
import json
import logging

# Create your views here.

from django.urls import reverse
import platform
import netifaces as ni

class IndexView(generic.ListView):
    template_name = 'visaweb/index.html'
    context_object_name = 'device_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return VisaDevice.objects.all()

class DetailView(generic.DetailView):
    model = VisaDevice
    context_object_name = 'device'
    template_name = 'visaweb/detail.html'
    slug_field = 'alias'

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['log'] = self.get_object().log()
        return context

    # def get_object(self):
    #     return get_object_or_404(VisaDevice, alias=request.session['device_alias'])

class ResultsView(generic.DetailView):
    model = VisaEvent
    context_object_name = 'action'
    template_name = 'visaweb/results.html'


    def get_context_data(self, **kwargs):
        context = super(ResultsView, self).get_context_data(**kwargs)
        context['device'] = self.get_object().session
        return context

# def index(request):
#     hostname = platform.node()
#     device_list = VisaDevice.objects.all()
#
#     nics = []
#     for interface_name in ni.interfaces():
#         nics.append({
#             'name': interface_name,
#             'details': ni.ifaddresses(interface_name)
#         })
#
#     context = {
#         'device_list': device_list,
#         'hostname': hostname,
#         'network_interfaces': nics
#     }
#     return render(request, 'visaweb/index.html', context)
#
#
# def detail(request, device_alias):
#     try:
#         device = VisaDevice.objects.get(alias=device_alias)
#         log = device.log()
#     except VisaDevice.DoesNotExist:
#         raise Http404("Device does not exist")
#     return render(request, 'visaweb/detail.html', { 'device': device, 'log': log })

def spectrum(request, device_alias):
    response = "Spectrum of %s."
    return HttpResponse(response % device_alias)

def waterfall(request, device_alias):
    return HttpResponse("Waterfall of %s." % device_alias)

# def results(request, device_alias, event_id):
#     device = get_object_or_404(VisaDevice, alias=device_alias)
#     event = get_object_or_404(VisaEvent, pk=event_id)
#     return render(request, 'visaweb/results.html', {'device': device, 'action': event})

def read(request, device_alias):
    device = get_object_or_404(VisaDevice, alias=device_alias)
    log = device.log()
    try:
        command = request.POST['command']
        logging.info('VISA: %s read %s' % (device_alias, command))
    except (KeyError, VisaDevice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'visaweb/detail.html', {
            'device': device,
            'log': log,
            'error_message': "Wrong VISA message."
        })
    else:
        e = VisaDevice.objects.get(alias=device_alias).read(
            request=command,
            response='NO VISA',
            success=False)
        return HttpResponseRedirect(reverse('visaweb:results', args=(e.id,)))

def write(request, device_alias):
    device = get_object_or_404(VisaDevice, alias=device_alias)
    log = device.log()
    try:
        command = request.POST['command']
        logging.info('VISA: %s write %s' % (device_alias, command))
    except (KeyError, VisaDevice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'visaweb/detail.html', {
            'device': device,
            'log': log,
            'error_message': "Wrong VISA message."
        })
    else:
        e = VisaDevice.objects.get(alias=device_alias).write(
            request=command,
            response='NO VISA',
            success=False)
        return HttpResponseRedirect(reverse('visaweb:results', args=(e.id,)))

def query(request, device_alias):
    device = get_object_or_404(VisaDevice, alias=device_alias)
    log = device.log()
    try:
        command = request.POST['command']
        logging.info('VISA: %s query %s' % (device_alias, command))
    except (KeyError, VisaDevice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'visaweb/detail.html', {
            'device': device,
            'log': log,
            'error_message': "Wrong VISA message."
        })
    else:
        e = VisaDevice.objects.get(alias=device_alias).query(
            request=command,
            response='NO VISA',
            success=False)
        return HttpResponseRedirect(reverse('visaweb:results', args=(e.id,)))