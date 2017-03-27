import netaddr
import json

from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.contrib.auth.models import User
from django.core import serializers
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError

from constellation_base.models import GlobalTemplateSettings

from .forms import DeviceForm

from .models import Device


@login_required
def view_show_user(request):
    '''Return the base template that will call the API to display
    the '''
    template_settings_object = GlobalTemplateSettings(allowBackground=False)
    template_settings = template_settings_object.settings_dict()
    form = DeviceForm(initial={"owner": request.user})
    username = request.user.username

    return render(request, 'constellation_devicemanager/view-list.html', {
        'template_settings': template_settings,
        'form': form,
        'username': username,
    })


@login_required
def view_dashboard(request):
    '''Return a card that will appear on the main dashboard'''

    return render(request, 'constellation_devicemanager/dashboard.html')


def api_v1_device_add(request):
    deviceForm = DeviceForm(request.POST or None)
    if (request.POST and
        deviceForm.is_valid() and (
            request.user == deviceForm.cleaned_data['owner'] or
            request.user.is_staff)):
        # only do things if the form checks out.  The 'owner' value
        # must either match that of the user that is submitting the
        # form, or the form must be submitted by a user that has the
        # staff designation.

        mac = None
        try:
            # We define this inline so that we get nice macs out
            class MACCustomFormat(netaddr.mac_unix):
                word_fmt = '%.2X'
            mac = netaddr.EUI(deviceForm.cleaned_data['MAC'],
                              dialect=MACCustomFormat)
        except netaddr.core.AddrFormatError as e:
            return HttpResponseBadRequest("Bad address format")

        # At this point we have a mac address, and a user that is
        # authorized to add it, lets go ahead and construct the object
        newDevice = Device()
        newDevice.MAC = str(mac)

        newDevice.name = deviceForm.cleaned_data['name']
        newDevice.hostname = deviceForm.cleaned_data['hostname']

        if request.user == User.objects.get(username=deviceForm.cleaned_data['owner']):
            newDevice.owner = request.user
        else:
            newDevice.owner = User.objects.get(username=deviceForm.cleaned_data['owner'])

        try:
            newDevice.clean()
        except ValidationError:
            return HttpResponseBadRequest("Invalid Form Data")
        newDevice.save()
        return HttpResponse("Device saved successfully")
    else:
        return HttpResponseBadRequest("Invalid Form Data")


def api_v1_device_delete(request, deviceMAC):
    device = get_object_or_404(Device, pk=deviceMAC)
    device.delete()
    return HttpResponse("{0} was deleted".format(deviceMAC))


def api_v1_device_show_user(request, owner):
    devices = Device.objects.filter(owner=User.objects.get(username=owner))
    devicesJSON = serializers.serialize("json", devices)
    return HttpResponse(devicesJSON)


def api_v1_device_show_all(request):
    devices = Device.objects.all()
    deviceList = []
    for device in devices:
        d = {}
        d["MAC"] = device.MAC
        d["owner"] = device.owner.username
        d["name"] = device.name
        d["hostname"] = device.hostname
        deviceList.append(d)
    return HttpResponse(json.dumps(deviceList))
