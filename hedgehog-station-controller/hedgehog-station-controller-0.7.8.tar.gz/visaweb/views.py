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

import rpc.client as client
import visualization.visualizer as vis
import logging

configuration = {
    'mq': {
        'host': 'box.cherubits.hu',
        # 'host': 'localhost',
        'port': 5672,
        'username': 'hedgehog',
        # 'username': 'guest',
        'password': 'qwe123',
        # 'password': 'guest',
        'exchange': 'visa_rpc'
    }
}

rpcClient = client.VisaRpcClient(
    exchange=configuration['mq']['exchange'],
    host=configuration['mq']['host'],
    port=configuration['mq']['port'],
    username=configuration['mq']['username'],
    password=configuration['mq']['password'])

logging.info('VISA client created.')


class IndexView(generic.ListView):
    template_name = 'visaweb/index.html'
    context_object_name = 'device_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return VisaDevice.objects.all()

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['hostname'] = platform.node()
        nics = []
        for interface_name in ni.interfaces():
            nics.append({
                'name': interface_name,
                'details': ni.ifaddresses(interface_name)
            })
        context['network_interfaces'] = nics
        context['visa_connections'] = rpcClient.list({})
        return context

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

        heatmapVisualizer = vis.Heatmap(properties={
            'title': 'Custom SVG',
            'width': 640,
            'height': 480,
            'frequency_span': 40,
            'frequency_center': 100,
            'amplitude_reference': 0,
            'amplitude_span': -100
        })
        context['heatmap'] = heatmapVisualizer.show(json.loads(self.get_object().response))

        spectrumVisualizer = vis.Spectrum(properties={
            'title': 'Custom SVG',
            'width': 640,
            'height': 480,
            'frequency_span': 40,
            'frequency_center': 100,
            'amplitude_reference': 0,
            'amplitude_span': -100
        })
        context['spectrum'] = spectrumVisualizer.show(json.loads(self.get_object().response))

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
    # rheatmapVisualizer = vis.Heatmap(properties={
    #     'title': 'Custom SVG',
    #     'width': 640,
    #     'height': 480,
    #     'frequency_span': 40,
    #     'frequency_center': 100,
    #     'amplitude_reference': 0,
    #     'amplitude_span': -100
    # })
    #
    # dataResponse = heatmapVisualizer.show(visaResponse)

    return HttpResponse('sss')

def waterfall(request, device_alias):
    return HttpResponse("Waterfall of %s." % device_alias)

# def results(request, device_alias, event_id):
#     device = get_object_or_404(VisaDevice, alias=device_alias)
#     event = get_object_or_404(VisaEvent, pk=event_id)
#     return render(request, 'visaweb/results.html', {'device': device, 'action': event})

def attach(request):
    # device = get_object_or_404(VisaDevice, alias=device_alias)
    address = request.POST['address']
    alias = request.POST['alias']

    device = VisaDevice(active=True, connected=True, alias=alias, address=address)
    device.save()

    aliasRequest = {}
    aliasRequest[alias] = address
    rpcClient.alias(aliasRequest)

    # device.alias = address
    # device.address = address
    # device.connected = True
    # device.save()
    return HttpResponseRedirect(reverse('visaweb:index'))

def read(request, device_alias):
    device = get_object_or_404(VisaDevice, alias=device_alias)
    log = device.log()
    try:
        visaRequest = request.POST['command']
        logging.info('VISA: %s read %s' % (device_alias, visaRequest))

    except (KeyError, VisaDevice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'visaweb/detail.html', {
            'device': device,
            'log': log,
            'error_message': "Wrong VISA message."
        })
    else:
        try:
            aliasRequest = {}
            aliasRequest['agilent_hp_8920B'] = 'GPIB0::8::INSTR'
            rpcClient.alias(aliasRequest)

            visaResponse = rpcClient.query({
                'alias': device_alias,
                'command': visaRequest
            })
        except (Exception):
            e = VisaDevice.objects.get(alias=device_alias).read(
                request=visaRequest,
                response=json.dumps(visaResponse),
                success=False)
        else:
            e = VisaDevice.objects.get(alias=device_alias).read(
                request=visaRequest,
                response=json.dumps(visaResponse),
                success=True)

        return HttpResponseRedirect(reverse('visaweb:results', args=(e.id,)))

def write(request, device_alias):
    device = get_object_or_404(VisaDevice, alias=device_alias)
    log = device.log()
    try:
        visaRequest = request.POST['command']
        logging.info('VISA: %s write %s' % (device_alias, visaRequest))
    except (KeyError, VisaDevice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'visaweb/detail.html', {
            'device': device,
            'log': log,
            'error_message': "Wrong VISA message."
        })
    else:
        try:
            aliasRequest = {}
            aliasRequest['agilent_hp_8920B'] = 'GPIB0::8::INSTR'
            rpcClient.alias(aliasRequest)

            visaResponse = rpcClient.query({
                'alias': device_alias,
                'command': visaRequest
            })
        except (Exception):
            e = VisaDevice.objects.get(alias=device_alias).write(
                request=visaRequest,
                response=json.dumps(visaResponse),
                success=False)
        else:
            e = VisaDevice.objects.get(alias=device_alias).write(
                request=visaRequest,
                response=json.dumps(visaResponse),
                success=True)

        return HttpResponseRedirect(reverse('visaweb:results', args=(e.id,)))

def query(request, device_alias):
    device = get_object_or_404(VisaDevice, alias=device_alias)
    log = device.log()
    try:
        visaRequest = request.POST['command']
        logging.info('VISA: %s query %s' % (device_alias, visaRequest))


    except (KeyError, VisaDevice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'visaweb/detail.html', {
            'device': device,
            'log': log,
            'error_message': "Wrong VISA message."
        })
    else:
        try:
            aliasRequest = {}
            aliasRequest['agilent_hp_8920B'] = 'GPIB0::8::INSTR'
            rpcClient.alias(aliasRequest)

            visaResponse = rpcClient.query({
                'alias': device_alias,
                'command': visaRequest
            })
            e = VisaDevice.objects.get(alias=device_alias).query(
                request=visaRequest,
                response=json.dumps(visaResponse),
                success=True)
        except (Exception):
            e = VisaDevice.objects.get(alias=device_alias).query(
                request=visaRequest,
                response=json.dumps(visaResponse),
                success=False)

        return HttpResponseRedirect(reverse('visaweb:results', args=(e.id,)))