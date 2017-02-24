#!/usr/bin/env python
# -*- coding: utf-8 -*-
import default
import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from connections import HOST, IO_PORT
from django.core.signals import request_finished, got_request_exception
import os
from datetime import datetime


class DefaultTrigger(default.Trigger):
    exlude = []
    types = []

    def get_url(self, instance):
        return reverse('admin:%s_%s_change' % (instance._meta.app_label,  instance._meta.model_name),  args=[instance.pk])
    # end def

    def get_exclude(self, instance):
        return self.exlude
    # end def

    def create(self, instance):
        super(DefaultTrigger, self).create(instance)
        data = self.get_data(instance)
        send_to = []
        for type_ in self.types:
            send_to.append(type_.__name__)
        # end for
        url = self.get_url(instance)

        obj = {
            "data": data,
            "url": url,
            "html": self.message % data,
            "_send_to_": send_to,
            "exclude": self.get_exclude(instance)
        }

        if self.has_plugin('ioplugin'):
            self.emit_by('save', obj, 'ioplugin')
        # end if

        if self.has_plugin('smtpplugin'):
            emails = []
            for type_ in self.types:
                users = type_.objects.all()
                for user in users:
                    if user.email != '' and not user.email in emails:
                        emails.append(user.email)
                    # end if
                # end for
            # end for
            obj['data']['emails'] = emails
            self.emit_by('create', obj, 'smtpplugin')
        # end if
    # end def
# end class


class ResendTrigger(default.Trigger):

    def get_url(self, instance):
        return reverse('admin:%s_%s_change' % (instance._meta.app_label,  instance._meta.model_name),  args=[instance.pk])
    # end def

    def update(self, instance):
        super(ResendTrigger, self).update(instance)
        data = self.get_data(instance)
        send_to = []
        for type_ in self.types:
            send_to.append(type_.__name__)
        # end for

        obj = {
            "data": data,
            "url": self.get_url(instance),
            "html": self.message % data,
            "_send_to_": send_to
        }

        if self.has_plugin('smtpplugin') and hasattr(instance, 'resend') and instance.resend:
            emails = []
            for type_ in self.types:
                users = type_.objects.all()
                for user in users:
                    if user.email != '' and not user.email in emails:
                        emails.append(user.email)
                    # end if
                # end for
            # end for
            obj['data']['emails'] = emails
            self.emit_by('create', obj, 'smtpplugin')
        # end if
    # end def
# end class


class UserTrigger(default.Trigger):

    def get_type(self, instance):
        return self.type
    # end  def

    def get_url(self, instance):
        return reverse('admin:%s_%s_change' % (instance._meta.app_label,  instance._meta.model_name),  args=[instance.pk])
    # end def

    def save(self, instance):
        super(UserTrigger, self).save(instance)
        data = self.get_data(instance)
        url = self.get_url(instance)
        obj = {
            "data": data,
            "url": url,
            "html": self.message % data,
            "webuser": self.get_webuser(instance)
        }

        if self.has_plugin('ioplugin'):
            obj["_send_to_"] = self.get_type(instance).__name__
            self.emit_by('user', obj, 'ioplugin')
        # end if

        with open(os.path.join(BASE_DIR, 'io_plugin.log'), 'a+') as log:
            log.write("%s sended to: %s\n" % (datetime.now(), obj, ))
            log.close()
        # end with

        if self.has_plugin('smtpplugin'):
            emails = []
            for type_ in self.types:
                users = type_.objects.all()
                for user in users:
                    if user.email != '' and not user.email in emails:
                        emails.append(user.email)
                    # end if
                # end for
            # end for
            obj['data']['emails'] = emails
            self.emit_by('save', obj, 'smtpplugin')
        # end if
    # end def
# end class


class CronTrigger(default.Trigger):

    def get_url(self, instance):
        return reverse('admin:%s_%s_change' % (instance._meta.app_label,  instance._meta.model_name),  args=[instance.pk])
    # end def

    def save(self, instance):
        super(CronTrigger, self).save(instance)
        data = self.get_data(instance)
        send_to = []
        for type_ in self.types:
            send_to.append(type_.__name__)
        # end for
        url = self.get_url(instance)
        obj = {
            "data": data,
            "url": url,
            "cron": self.get_cron(instance),
            "html": self.message % data,
            "class": self.__class__.__name__,
            "owner": str(instance.pk),
            "_send_to_": send_to
        }
        if self.has_plugin('ioplugin'):
            self.emit_by('cron', obj, 'ioplugin')
        # end if
    # end def
# end class


class HolyDayTrigger(CronTrigger):
    message = u"Hoy es el cumpleaños de %(nombre)s"

    def get_cron(self, instance):
        #       s m  h  d m  s
        return "0 6 11 %s %s *" % (instance.fecha_nacimiento.day, instance.fecha_nacimiento.month)
    # end def

# end class

class E500Trigger(UserTrigger):
    types = []
    message = u"""Error 500"""

    def get_webuser(self, request):
        if hasattr(request, 'user'):
            return [request.user]
        # end if
        return "No user"
    # end def

    def get_url(self, request):
        return request.path
    # end def

    def get_data(self, request):
        data = request.__dict__
        data['include'] = 'luismiguel.mopa@gmail.com'
        return data
    # end def
# edn class

def request_exception(sender, **kwargs):
    """
    trigger = E500Trigger()
    e500 = E500SMTPPlugin()
    e500.init(kwargs['request'])
    trigger.plugins['smtpplugin'] = e500
    trigger.create(kwargs['request'])
    """
    pass
# end def

got_request_exception.connect(request_exception)
