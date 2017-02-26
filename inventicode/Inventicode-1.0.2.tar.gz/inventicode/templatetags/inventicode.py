# -*- coding: utf-8 -*-
import base64
import io

import barcode
import qrcode.image.svg
from django.template import Library
from django.utils.safestring import mark_safe

__author__ = 'Matthieu Gallet'

register = Library()


@register.filter
def base64_url(value, filetype='image/svg+xml'):
    return mark_safe('data:%s;base64,%s' % (filetype, base64.b64encode(value).decode()))


@register.filter
def bar_code(value, kind='ean13'):
    fd = io.BytesIO()
    encoder = barcode.get_barcode_class(kind)
    encoder(value).write(fd)
    return fd.getvalue()


@register.filter
def qr_code(value):
    factory = qrcode.image.svg.SvgPathImage
    img = qrcode.make(value, image_factory=factory)
    fd = io.BytesIO()
    img.save(fd)
    return fd.getvalue()


@register.filter
def unit(value: float):
    if int(value) == value:
        return '%smm' % value
    return '%spt' % int(value * 72 / 25.4)
