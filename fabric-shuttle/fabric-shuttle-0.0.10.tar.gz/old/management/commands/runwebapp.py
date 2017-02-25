from importlib import import_module
import os
import signal
import subprocess

from django.conf import settings
from django.contrib.staticfiles.management.commands.runserver import Command as RunserverCommand
from utils.colors import bold, red
from utils.urls import static_serve_url

__webapp_process = None

def _signal_handler(sig, frame):
	"""Kill the runwebapp process on Control-C. Probably redundant because child processes should be automatically killed by the OS."""
	signal.signal(signal.SIGINT, signal.SIG_IGN)
	if __webapp_process:
		__webapp_process.kill()
	import sys
	sys.exit(0)

def get_webapp_taskrunner(webapp_root):
	"""Return gulp or gruntfile as the taskrunner if applicable."""
	if webapp_root.endswith('/'):
		parent = webapp_root.rsplit('/', 2)[0]
	else:
		parent = webapp_root.rsplit('/', 1)[0]
	task_runner = None
	if os.path.exists(parent + '/Gruntfile.js') or os.path.exists(parent + '/Gruntfile.coffee'):
		task_runner = 'grunt'
	elif os.path.exists(parent + '/gulpfile.js') or os.path.exists(parent + '/gulpfile.coffee'):
		task_runner = 'gulp'
	return parent, task_runner

def run_webapp(webapp_root):
	"""Run a webapp, based on a WEBAPP_ROOT setting.

	Assumes that the webapp_root is a build subdirectory to a parent project with a grunt file.
	"""
	global __webapp_process
	parent, task_runner = get_webapp_taskrunner(webapp_root)
	if task_runner:
		print bold('Running %s ...' % parent)
		cwd = os.getcwd()
		os.chdir(parent)
		__webapp_process = subprocess.Popen([task_runner, 'runwebapp'])
		os.chdir(cwd)

runwebapp_help = """
Starts a development web server for running a project, static files, and a single static web app (just like adding an additional STATIC_ROOT and STATIC_URL only for a specific web app with the settings below).
If a Gruntfile or gulpfile is in the parent directory, the webapp will first call the runwebapp task in the background, this should build, watch, and setup a livereload server.
The only possible non-development webapp setup is hosting on S3, with DNS pointing to the S3 bucket, and S3 redirecting 404, 403 to the django host if needed to share the same domain.
Currently, fab deployment will not automatically setup or configure the S3 bucket for the webapp

Requests for the non-development webapp must first go through the S3 bucket because:
  - Redirecting (rewrite) from nginx to S3 cannot be done because '/' is a typical webapp url, but '/' is needed for django
  - Serving statically (alias) from nginx cannot be done because webapps will typically reference other static files not under their directory, which this command and fab deploy resolves
  - Statically serving files with django, like this command is bad for non-development setups

Settings:
  WEBAPP_ROOT
                        e.g. os.path.abspath('.') + '/projectswebapp/build/'
                        Only used with this command and fab deploy
                        Will be converted to the correct path, like MEDIA_ROOT, when deploying with fab

  WEBAPP_URL
                        '/' (default) or '/projectswebapp/' used with this command only

  WEBAPP_INDEX
                        'index.html' (default) or some other filename
                        The index file to use when a directory is requested
                        For use with this command only
"""

class Command(RunserverCommand):
	help = runwebapp_help

	def handle(self, *args, **options):
		"""Stardard handle method. This runs on both the parent autoreload process and the main child process."""

		# Only run the taskrunner once from the parent autoreload process (where RUN_MAIN is None) that watches files and launches/relaunches the main webserver child process
		# https://github.com/django/django/blob/master/django/utils/autoreload.py
		if not os.environ.get("RUN_MAIN"):
			if not hasattr(settings, 'WEBAPP_ROOT') or not hasattr(settings, 'WEBAPP_URL'):
				print red('Error: There is no web app setup for this project!', True)
				raise UserWarning

			# Run webapp if applicable
			signal.signal(signal.SIGINT, _signal_handler)
			run_webapp(settings.WEBAPP_ROOT)

		return super(Command, self).handle(*args, **options)

	def get_handler(self, *args, **options):
		"""Return the RunserverCommand get_handler. This doesn't run on the parent autoreload process."""

		# Modify the urls
		webapp_url = getattr(settings, 'WEBAPP_URL', '/')
		module = import_module(settings.ROOT_URLCONF)
		module.urlpatterns.append(static_serve_url(webapp_url, settings.WEBAPP_ROOT, view='utils.views.webapp_serve'))

		return super(Command, self).get_handler(*args, **options)
