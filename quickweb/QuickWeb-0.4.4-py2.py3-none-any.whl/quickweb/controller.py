# -*- coding: utf-8 -*-
import re
import sys
import cherrypy

this = sys.modules[__name__]
this.app_root = None

def set_approot(root_node):
    this.app_root = root_node
    return this.app_root


def attach(controller_path_name, controller_obj):
    controller_path_name = controller_path_name.strip("/")
    if controller_path_name == '':  # No path provided, override the index handler
        this.app_root.index = controller_obj.index
    else:
        setattr(this.app_root, controller_path_name, controller_obj)

def publish(func=None, *args):
    return cherrypy.expose(func, *args)


def redirect(url):
    raise cherrypy.HTTPRedirect(url)


def get_cookie(name, default_value=None):
    def unescape(s):
        m = re.match(r'^"(.*)"$', s)
        s = m.group(1) if m else s
        return s.replace("\\\\", "\\")

    if cherrypy.request.cookie.has_key(name):
        return unescape(cherrypy.request.cookie[name].value).decode('unicode-escape')
    else:
        return default_value


def get_session_value(name, default_value=None):
    # pylint: disable=E1101
    if name in cherrypy.session:
        return cherrypy.session[name]
    else:
        return default_value


def set_session_value(name, value):
    # pylint: disable=E1101
    cherrypy.session[name] = value


def set_cookie(name, value, path='/', max_age=3600, version=1):
    cookie = cherrypy.response.cookie
    cookie[name] = value.encode('unicode-escape')
    cookie[name]['path'] = path
    cookie[name]['max-age'] = max_age
    cookie[name]['version'] = version


def delete_cookie(name):
    cherrypy.response.cookie[name] = 'deleting'
    cherrypy.response.cookie[name]['expires'] = 0


def set_response(name, value):
    cherrypy.response.headers[name] = value


def method():
    return cherrypy.request.method


def params():
    return cherrypy.request.params


def controller_url():
    """
    @return: the current request url
    """
    return cherrypy.request.path_info


def controller_path():
    """
    @return: the current request url
    """
    return cherrypy.request.path_info.split('/')


def get_config():
    return cherrypy.config
