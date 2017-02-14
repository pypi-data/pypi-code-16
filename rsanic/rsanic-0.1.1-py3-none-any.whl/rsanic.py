#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from sanic import Sanic
from sanic.response import json, html, text
from jinja2 import Environment, FileSystemLoader
import importlib


class Rsanic:

    routes = {}

    def __init__(self, config, routes, name=None, error_handler=None):

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
        self.config = config

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
            handler = {'controller': 'www.home.NotFound', 'return_type': 'html'}
        try:
            return_type = handler['return_type']
        except KeyError:
            return_type = 'html'
        module_name, class_name = handler['controller'].rsplit(".", 1)
        module_path = handler['controller']
        controller_obj = getattr(importlib.import_module(module_path), class_name.title())
        controller = controller_obj()
        controller.application_global()
        controller.controller_global()
        controller_response = controller.invoke(args)
        if return_type == 'html':
            env = Environment()
            loader = FileSystemLoader(self.config['app_dir'] + '/templates')
            env.loader = loader
            env.globals['config'] = self.config
            template_path = handler['controller'].replace('.', '/') + '.html'
            template = env.get_template(template_path)
            return html(template.render(response=controller_response))
        elif return_type == 'json':
            return json(controller_response)
        else:
            return text(controller_response)
