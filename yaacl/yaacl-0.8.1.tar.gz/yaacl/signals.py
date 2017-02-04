# -*- coding:utf-8 -*-
from django.dispatch import Signal

__author__ = 'Daniel Alkemic Czuba <dc@danielczuba.pl>'

register_resource = Signal(
    providing_args=['resource', 'name'],
)
