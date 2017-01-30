"""
tmpld.cli.main
~~~~~~~~~~~~~~

Cement CLI main app logic for tmpld.

:copyright: (c) 2016 by Joe Black.
:license: Apache2.
"""

import os
import sys

from cement.core.foundation import CementApp
from cement.core.controller import CementBaseController, expose

import pyrkube
import pycaps

from ..core import template, environment
from . import handlers


class TmpldController(CementBaseController):
    class Meta:
        label = 'base'
        arguments = [
            (['files'],
             dict(help='template files to render',
                  action='store',
                  nargs='+'))
        ]

    def _get_ext(self, name, config):
        if name == 'kube':
            kube = pyrkube.KubeAPIClient(
                config['environment'],
                config['namespace'],
                config['domain'])
            self.app.log.debug('Got kubernetes api client: %s', kube)
            return kube
        elif name == 'caps':
            return pycaps.get_caps()

    def _get_config(self):
        config = self.app.config.get_section_dict('tmpld')
        self.app.log.debug('Using configuration: %s', config)
        return config

    def _get_extensions(self, config):
        extensions = {name: self._get_ext(name, config)
                      for name in config['exts']}
        self.app.log.debug('Got extensions: %s', extensions)
        return extensions

    def _get_template_environment(self, extensions):
        template_env = environment.TemplateEnvironment(extensions)
        self.app.log.debug('Got Jinja environment: %s', template_env)
        return template_env

    def _get_templates(self):
        files = self.app.pargs.files
        self.app.log.debug('Got files: %s', files)
        templates = [template.Template(file) for file in files]
        self.app.log.debug('Got templates: %s', templates)
        return templates

    def render_templates(self, environment, templates):
        for tmp in templates:
            self.app.log.debug('Rendering: %s > %s', tmp.file, tmp.target)
            self.app.render('Rendering: %s > %s' % (tmp.file, tmp.target))
            environment.render(tmp)
            self.app.render(tmp.print(as_string=True))
            tmp.write()

    @expose(hide=True)
    def default(self):
        self.app.log.debug('CLI arguments: %s', self.app.pargs)
        config = self._get_config()
        extensions = self._get_extensions(config)
        template_env = self._get_template_environment(extensions)
        templates = self._get_templates()
        self.render_templates(template_env, templates)


class TmpldApp(CementApp):
    class Meta:
        label = 'tmpld'
        description = 'Renders jinja2 templates using kubernetes api objects.'
        base_controller = TmpldController
        log_handler = handlers.KubeWaitLogHandler
        output_handler = handlers.StandardOutputHandler
        config_defaults = {
            'tmpld': dict(
                environment=os.getenv('TMPLD_ENVIRONMENT', 'production'),
                namespace=os.getenv('TMPLD_NAMESPACE', 'default'),
                domain=os.getenv('TMPLD_DOMAIN', 'cluster.local'),
                exts=os.getenv('TMPLD_EXTENSIONS', 'kube,caps').split(',')
            ),
            'log.kwlogging': dict(
                level=os.getenv('TMPLD_LOG_LEVEL', 'DEBUG')
            )
        }


def main(args=None):
    args = args or sys.argv[1:]
    with TmpldApp(argv=args) as app:
        app.run()
