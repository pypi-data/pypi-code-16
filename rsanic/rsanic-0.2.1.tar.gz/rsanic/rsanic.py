#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from sanic import Sanic
from sanic.response import json, html, text
from jinja2 import Environment, FileSystemLoader
from jinja2.bccache import FileSystemBytecodeCache
import importlib


class Rsanic:

    routes = {}

    container = None

    def __init__(self, container, name=None, error_handler=None):
        self.container = container
        self.config = container.config()
        routes = container.routes()
        app = Sanic(name, error_handler=error_handler)
        for route in routes:
            url = route[1]
            try:
                return_type = route[3]
                return_type = return_type.lower()
            except (KeyError, IndexError):
                return_type = 'html'
            self.routes[url] = {'controller': route[2], 'return_type': return_type}
            if route[0].__class__ is dict:
                methods = route[0]
            else:
                methods = {route[0]}
            app.add_route(self.handler, route[1], methods=methods)
        self.app = app

    def run(self):
        self.app.run(host=self.config['host'], port=self.config['port'], debug=self.config['debug'])

    async def handler(self, request, **args):
        sys.path.append(self.config['app_dir'] + '/controllers')
        url = request.url
        route_data = self.app.router.get(request)
        for key, value in route_data[2].items():
            url = url.replace(value, '<' + key + '>')
        try:
            handler = self.routes[url]
        except KeyError:
            handler = {'controller': self.config.not_found_method, 'return_type': self.config.default_return_type}
        try:
            return_type = handler['return_type']
        except KeyError:
            return_type = self.config.default_return_type
        module_name, class_name = handler['controller'].rsplit(".", 1)
        module_path = handler['controller']
        controller_obj = getattr(importlib.import_module(module_path), class_name.title())
        controller = controller_obj(container=self.container, request=request)
        controller.application_global()
        controller.controller_global()
        controller_response = controller.invoke(args)
        controller.close()
        if return_type == 'html':
            return html(self.html_response(handler, controller_response))
        elif return_type == 'json':
            return json(controller_response)
        else:
            return text(controller_response)

    def html_response(self, handler, controller_response):
        bcc = FileSystemBytecodeCache()
        loader = FileSystemLoader(self.config['app_dir'] + '/templates')
        jinja = Environment(bytecode_cache=bcc, loader=loader)
        jinja.globals['config'] = self.config
        template_path = handler['controller'].replace('.', '/') + '.html'
        template = jinja.get_template(template_path)
        return template.render(response=controller_response)
