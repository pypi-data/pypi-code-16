#!/usr/bin/env python
# -*- coding: utf-8 -*-
# for AthenticationError:
# https://www.google.com/settings/u/1/security/lesssecureapps

from django import forms
from socketIO_client import SocketIO
from django.contrib.auth.models import User
from django.contrib import admin
import time

from django.core import mail as smtpplugin
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from threading import Thread
from django.db.models.signals import post_save
from django.db import models
from django.dispatch import receiver
from django.template.loader import render_to_string

from datetime import datetime
import os
from django.conf import settings

class Trigger(object):
    model = None
    events = {'save': 'all', 'create': 'all', 'update': 'all'}

    def __init__(self, *args, **kwargs):
        self.plugins = {}
    # end def

    def init(self, request):
        self.request = request
        for plugin in self.plugins:
            self.plugins[plugin].init(request)
        # end def
    # end def

    def add_plugin(self, plugin):
        self.plugins[plugin.name] = plugin()
    # end def

    def has_plugin(self, plugin):
        return plugin in self.plugins
    # end def

    def save(self, instance):
        self.auto_emit('save', instance)
    # end def

    def create(self, instance):
        self.auto_emit('create', instance)
    # end def

    def update(self, instance):
        self.auto_emit('update', instance)
    # end def

    def auto_emit(self, event, instance):
        if event in self.events:
            if self.events[event] == 'all':
                self.emit(event, instance)
            else:
                self.emit_by(event, instance, self.event[event])
            # end if
        # end if
    # end def

    def emit_by(self, event, instance, by):
        self.plugins[by].emit(event, instance)
    # end def

    def emit(self, event, instance):
        for plugin in self.plugins:
            self.emit_by(event, instance, plugin)
        # end def
    # end def

# end class


class triggers(object):
    _registry = []
    times = {}

    @classmethod
    def register(cls, trigger, plugins=[]):
        trg = trigger()
        for plugin in plugins:
            trg.add_plugin(plugin)
        # end for
        cls._registry.append(trg)
        if isinstance(trg.model, list):
            for model in trg.model:
                cls.times[model] = 0
            # end for
        else:
            cls.times[trg.model] = 0
        # end if
    # end def

    @classmethod
    def get_registries(cls, model):
        registries = []
        for registry in cls._registry:
            if isinstance(registry, list):
                if model in registry.model:
                    registries.append(registry)
                # end if
            else:
                if model == registry.model:
                    registries.append(registry)
                # end if
            # end if
        # end for
        return registries
    # end def
# end class


def save_model(sender, instance, **kwargs):
    registries = triggers.get_registries(sender)
    for registry in registries:
        registry.init(triggers.request)
        registry.save(instance)
        if kwargs['created']:
            registry.create(instance)
        else:
            registry.update(instance)
        # end if
    # end for
# end def

post_save.connect(save_model, dispatch_uid="save_model_for_all")

class Middleware(object):

    def __init__(self, get_response):
        self.get_response = get_response
    # end def

    def __call__(self, request, *args, **kwargs):
        triggers.request = request
        for model in triggers.times:
            triggers.times[model] = 0
        # end for
        response = self.get_response(request)
        return response
    # end def

# end class

class Plugin(object):

    def init(self, request):
        self.request = request
    # end def

    def emit(self, event, message):
        pass
    # end def
# end class