# -*- coding: utf-8 -*-
from PIL import Image
from django.conf import settings
from django.utils._os import safe_join
from django.utils.encoding import filepath_to_uri, python_2_unicode_compatible
from django.utils.safestring import mark_safe
import importlib
import os
import urlparse
from django.http.response import HttpResponse
import json
import sys

# @OG replace with import_string
# from django.utils.module_loading import import_string

class JSONResponse(HttpResponse):
    def __init__(self, content = {}, *args, **kwargs):
        kwargs['content_type'] = "application/json"
        super(JSONResponse, self).__init__(json.dumps(content), *args, **kwargs)

def get_class(class_path):
    module_name, class_name = class_path.rsplit(".", 1)
    return getattr(importlib.import_module(module_name), class_name)

# Images

@python_2_unicode_compatible
class BlankImage(object):
    def __init__(self):
        self.name = settings.CONGO_BLANK_IMAGE_FILENAME
        self.path = settings.CONGO_BLANK_IMAGE_PATH
        self.url = settings.CONGO_BLANK_IMAGE_URL

    def __str__(self):
        return self.get_path()

    def _get_size(self, max_width, max_height = None):
        if not max_height:
            max_height = max_width

        if not isinstance(max_width, int):
            max_width = settings.CONGO_DEFAULT_IMAGE_WIDTH

        if not isinstance(max_height, int):
            max_height = settings.CONGO_DEFAULT_IMAGE_HEIGHT

        return (max_width, max_height)

    def _resize(self, path, width, height):
        image = Image.open(self.get_path())
        image = image.resize((width, height), Image.ANTIALIAS)
        image.save(path)

        del image

    def render(self, max_width = None, max_height = None, **kwargs):
        url = self.get_url(max_width, max_height)

        width, height = self._get_size(max_width, max_height)
        css_class = kwargs.get('css_class', '')
        alt_text = kwargs.get('alt_text', '')

        html = """<img src="%s" width="%s" height="%s" class="%s" alt="%s" />""" % (url, width, height, css_class, alt_text)
        return mark_safe(html)

    def get_path(self, name = None):
        if not name:
            name = self.name
        return os.path.normpath(safe_join(self.path, name))

    def get_name(self, width, height):
        split = self.name.rsplit('.', 1)
        return '%s_%sx%s.%s' % (split[0], width, height, split[1])

    def get_url(self, max_width = None, max_height = None):
        width, height = self._get_size(max_width, max_height)
        name = self.get_name(width, height)
        path = self.get_path(name)

        if not os.path.isfile(path):
            try:
                self._resize(path, width, height)
            except IOError:
                self.get_path(name)

        return urlparse.urljoin(self.url, filepath_to_uri(name))

# Data structs

@python_2_unicode_compatible
class Message(object):
    DEBUG = 10
    INFO = 20
    SUCCESS = 25
    QUESTION = 26
    WARNING = 30
    ERROR = 40

    DEFAULT_TAGS = {
        DEBUG: 'debug',
        INFO: 'info',
        SUCCESS: 'success',
        QUESTION: 'question',
        WARNING: 'warning',
        ERROR: 'error',
    }

    CSS_CLASS_DICT = {
        DEBUG: 'debug',
        INFO: 'info',
        SUCCESS: 'success',
        QUESTION: 'question',
        WARNING: 'warning',
        ERROR: 'danger',
    }

    def __init__(self, level, message, extra_tags = ''):
        self.level = level
        self.message = message
        self.tags = self.DEFAULT_TAGS[level]

        if len(extra_tags):
            self.tags += " " + extra_tags

    def __str__(self):
        return self.message

    @classmethod
    def get_level_name(cls, level):
        return cls.DEFAULT_TAGS[level]

    @classmethod
    def get_level_by_css_class(cls, css_class):
        for key, val in cls.CSS_CLASS_DICT.items():
            if  css_class == val:
                return key
        return None

    @classmethod
    def get_level_css_class(cls, level):
        return cls.CSS_CLASS_DICT[level]

    @classmethod
    def render(cls, obj, **kwargs):
        # close (bool)
        close = kwargs.get('close', False)
        extra_tags = kwargs.get('extra_tags', '')

        level_css_class = cls.CSS_CLASS_DICT[obj.level]
        alert_class = "alert-%s" % level_css_class
        dismiss_class = "alert-dismissible" if close else ""
        fade_class = "fade in" if close else ""
        close_html = """<button type="button" class="close" data-dismiss="alert">&times;</button>""" if close else ""
        text_class = "text-%s" % level_css_class
        icon_class = "icon-%s" % level_css_class

        _extra_tags = obj.tags
        if len(_extra_tags) > len(level_css_class) and _extra_tags[-(len(level_css_class) + 1):] == " %s" % level_css_class:
            _extra_tags = _extra_tags[:-(len(level_css_class) + 1)]
        elif _extra_tags == level_css_class:
            _extra_tags = ''

        alert_class_set = "%s %s %s %s %s" % (alert_class, dismiss_class, fade_class, extra_tags, _extra_tags)
        alert_class_set = " ".join(alert_class_set.split())

        html = u"""
            <div class="alert %s">%s
              <div class="alert-icon %s"><i class="%s"></i></div>
              <div class="alert-body">%s</div>
            </div>
        """ % (alert_class_set, close_html, text_class, icon_class, obj.message)

        return mark_safe(html)

    @classmethod
    def debug(cls, message, extra_tags = ''):
        return cls(cls.DEBUG, message, extra_tags)

    @classmethod
    def info(cls, message, extra_tags = ''):
        return cls(cls.INFO, message, extra_tags)

    @classmethod
    def success(cls, message, extra_tags = ''):
        return cls(cls.SUCCESS, message, extra_tags)

    @classmethod
    def question(cls, message, extra_tags = ''):
        return cls(cls.QUESTION, message, extra_tags)

    @classmethod
    def warning(cls, message, extra_tags = ''):
        return cls(cls.WARNING, message, extra_tags)

    @classmethod
    def error(cls, message, extra_tags = ''):
        return cls(cls.ERROR, message, extra_tags)

@python_2_unicode_compatible
class MetaData(object):
    def __init__(self, request, title = u"", **kwargs):
        self.request = request

        self.title = title
        self.full_title = kwargs.get('full_title', None)
        self.subtitle = kwargs.get('subtitle', None)
        self.meta_title = kwargs.get('meta_title', None)
        self.meta_description = kwargs.get('meta_description', None)
        self.meta_image = kwargs.get('meta_image', None)
        self.canonical_url = kwargs.get('canonical_url', None)
        self.prev_url = kwargs.get('prev_url', None)
        self.next_url = kwargs.get('next_url', None)
        self.active = kwargs.get('active', None)
        self.breadcrumbs = kwargs.get('breadcrumbs', [])
        self.view = kwargs.get('view', None)
        self.append_default_title = kwargs.get('append_default_title', True)
        self.is_popup = kwargs.get('is_popup', None)
        self.ng_app = kwargs.get('ng_app', None)

        try:
            self.request_method = request.META.get('REQUEST_METHOD', None)
        except AttributeError:
            self.request_method = None

    def __str__(self):
        return self.get_meta_title()

    def get_full_title(self):
        return self.full_title or self.title

    def get_meta_title(self):
        meta_title = self.meta_title or self.title
        if self.append_default_title:
            if meta_title:
                return u"%s - %s" % (meta_title, settings.CONGO_DEFAULT_META_TITLE)
            else:
                return settings.CONGO_DEFAULT_META_TITLE
        return meta_title

    def get_meta_description(self):
        if self.meta_description is None:
            return settings.CONGO_DEFAULT_META_DESCRIPTION
        return self.meta_description

    def get_meta_image(self):
        if self.meta_image is None:
            return settings.CONGO_DEFAULT_META_IMAGE
        return self.meta_image

    def add_breadcrumb(self, label = None, url = None):
        if label is None:
            label = self.title
        if url is None:
            url = self.request.path
        self.breadcrumbs.append([label, url])

    def is_active(self, active):
        return self.active == active

class UserDevice(object):
    # device screen
    XS = 'xs'
    SM = 'sm'
    MD = 'md'
    LG = 'lg'

    # device type
    MOBILE = 'mobile'
    TABLET = 'tablet'
    PC = 'pc'

    # break_points
    BREAK_XS = 768
    BREAK_SM = 992
    BREAK_MD = 1200

    device_screen = LG
    device_type = None
    device_family = None

    os_family = None
    os_version = None

    browser_family = None
    browser_version = None

    is_mobile = False
    is_tablet = False
    is_pc = True

    is_touch_capable = False

    def __init__(self, request):
        # django_user_agents.middleware.UserAgentMiddleware required
        if hasattr(request, 'user_agent'):
            user_agent = request.user_agent

            # device_screen
            if user_agent.is_mobile:
                self.device_screen = self.XS
            elif user_agent.is_tablet:
                self.device_screen = self.SM

            # device_type
            if user_agent.is_mobile:
                self.device_type = self.MOBILE
            elif user_agent.is_tablet:
                self.device_type = self.TABLET
            elif user_agent.is_pc:
                self.device_type = self.PC

            self.device_family = user_agent.device.family

            self.os_family = user_agent.os.family
            self.os_version = user_agent.os.version_string

            self.browser_family = user_agent.browser.family
            self.browser_version = user_agent.browser.version_string

            self.is_mobile = user_agent.is_mobile
            self.is_tablet = user_agent.is_tablet
            self.is_pc = user_agent.is_pc

            self.is_touch_capable = user_agent.is_touch_capable

        device_screen = self.get_device_screen(request)
        if device_screen:
            self.device_screen = device_screen

    @property
    def is_xs(self):
        return self.device_screen == self.XS

    @property
    def is_sm(self):
        return self.device_screen == self.SM

    @property
    def is_md(self):
        return self.device_screen == self.MD

    @property
    def is_lg(self):
        return self.device_screen == self.LG

    @classmethod
    def set_device_screen(cls, request, screen_size):
        screen_size = int(screen_size)

        if screen_size <= cls.BREAK_XS:
            device_screen = cls.XS
        elif screen_size <= cls.BREAK_SM:
            device_screen = cls.SM
        elif screen_size <= cls.BREAK_MD:
            device_screen = cls.MD
        else:
            device_screen = cls.LG

        cached = cls.get_device_screen(request)

        if device_screen == cached:
            change = False
        else:
            request.session['device_screen'] = device_screen
            change = True

        return change

    @classmethod
    def get_device_screen(cls, request, dafault = None):
        return request.session.get('device_screen', dafault)
