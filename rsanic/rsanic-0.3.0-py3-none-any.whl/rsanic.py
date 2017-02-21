#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
import importlib
import logging
from datetime import datetime
from sanic import Sanic
from sanic.response import json, html, text
from sanic.log import log
from jinja2 import Environment, FileSystemLoader
from jinja2.bccache import FileSystemBytecodeCache
import asyncio


class Rsanic:

    routes = {}
    container = None
    app = None
    loop = None

    def __init__(self, container, name=None, error_handler=None):
        self.loop = container.loop() or asyncio.get_event_loop()
        if not logging.root.handlers and log.level == logging.NOTSET:
            formatter = logging.Formatter(
                "%(levelname)s: %(message)s")
            handler = logging.StreamHandler()
            handler.setFormatter(formatter)
            log.addHandler(handler)
            log.setLevel(logging.INFO)
        log.info('\n\t\t-------------------------------------------'
                 '\n\t\t              RSANIC loading               '
                 '\n\t\t-------------------------------------------')
        self.container = container
        self.config = container.config()
        routes = container.routes()
        log.info('Defining sanic app: %s\t', name)
        app = Sanic(name, error_handler=error_handler)
        if 'public' in self.config:
            log.info('Adding static folder %s at /public\t', self.config['public'])
            app.static('/public', self.config['public'])

        log.info('Adding routes:',)
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
            log.info('Methods: %s, URI: %s, Controller: %s, Return Type: %s', methods, route[1], route[2], return_type)
            app.add_route(self.handler, route[1], methods=methods)
        self.app = app
        log.info('RSENIC loaded')

    def run(self):
        self.app.run(host=self.config['host'], port=self.config['port'], debug=self.config['debug'], loop=self.loop)
        self.loop.close()

    async def handler(self, request, **args):

        sys.path.append(self.config['app_dir'] + '/controllers')
        url = request.url
        if 'log_access' in self.config and self.config['log_access']:
            log.info('%s\t%s\t %s', request.ip, datetime.now(), url)

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
        handler_parts = handler['controller'].rsplit(".", 1)
        module_path = handler['controller']
        controller_obj = getattr(importlib.import_module(module_path), handler_parts[1].title())
        controller = controller_obj(container=self.container, request=request)
        await controller.application_global()
        await controller.controller_global()
        controller_response = await controller.invoke(args)
        await controller.close()
        if return_type == 'html':
            return html(await self.html_response(handler, controller_response))
        elif return_type == 'json':
            return json(controller_response)
        else:
            return text(controller_response)

    async def html_response(self, handler, controller_response):
        bcc = FileSystemBytecodeCache()
        loader = FileSystemLoader(self.config['app_dir'] + '/templates')
        jinja = Environment(bytecode_cache=bcc, loader=loader, autoescape=True, auto_reload=True)
        jinja.globals['config'] = self.config
        template_path = handler['controller'].replace('.', '/') + '.html'
        template = jinja.get_template(template_path)
        controller_html = template.render(response=controller_response)
        app_template = '_default.html'
        if 'app_template' in controller_response:
            app_template = '_' + controller_response['app_template'] + '.html'
        main_template = jinja.get_template(app_template)
        app_data = {'content': controller_html}
        return main_template.render(app_data=app_data)

