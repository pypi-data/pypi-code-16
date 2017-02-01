# -*- coding:utf-8 -*-

from __future__ import unicode_literals
from future.utils import iteritems
from io import open

import os.path
from copy import copy

from statik.config import StatikConfig
from statik.utils import *
from statik.errors import *
from statik.models import StatikModel
from statik.views import StatikView
from statik.database import StatikDatabase
from statik.templating import StatikTemplateEngine

import statik.filters
import statik.tags

import logging
logger = logging.getLogger(__name__)

__all__ = [
    'StatikProject',
]


class StatikProject(object):

    VIEWS_DIR = "views"
    MODELS_DIR = "models"
    TEMPLATES_DIR = "templates"
    DATA_DIR = "data"
    TEMPLATETAGS_DIR = "templatetags"
    THEMES_DIR = "themes"
    ASSETS_DIR = "assets"
    CONFIG_FILE = "config.yml"

    def __init__(self, path, **kwargs):
        """Constructor.

        Args:
            path: The full filesystem path to the base of the project.
        """
        if 'config' in kwargs and isinstance(kwargs['config'], dict):
            logger.debug("Loading project configuration from constructor arguments")
            self.config = kwargs['config']
        else:
            self.config = None

        self.safe_mode = kwargs.pop('safe_mode', False)

        self.path, self.config_file_path = get_project_config_file(path, StatikProject.CONFIG_FILE)
        if (self.path is None or self.config_file_path is None) and self.config is None:
            raise MissingProjectConfig("No configuration could be found for project")

        logger.info("Project path configured as: %s" % self.path)

        self.models = {}
        self.template_engine = None
        self.views = {}
        self.db = None
        self.project_context = {}

    def generate(self, output_path=None, in_memory=False):
        """Executes the Statik project generator.

        Args:
            output_path: The path to which to write output files.
            in_memory: Whether or not to generate the results in memory. If True, this will generate the output
                result as a dictionary. If False, this will write the output to files in the output_path.

        Returns:
            If in_memory is True, this returns a dictionary containing the actual generated static content. If
            in_memory is False, this returns an integer indicating the number of files generated in the
            output path.
        """
        result = dict() if in_memory else 0
        try:
            result = self._generate(output_path=output_path, in_memory=in_memory)

        except Exception as e:
            logger.exception("Error caught: %s" % e)

        # done
        return result

    def _generate(self, output_path=None, in_memory=False):
        """Unsafe version of the generate() function. Does not perform exception handling."""
        result = dict() if in_memory else 0
        try:
            if output_path is None and not in_memory:
                raise ValueError("If project is not to be generated in-memory, an output path must be specified")

            self.config = self.config or StatikConfig(self.config_file_path)

            if self.config.encoding is not None:
                logger.info("Using encoding: %s" % self.config.encoding)
            else:
                logger.info("Using encoding: %s" % self.config.encoding)

            self.models = self.load_models()
            self.template_engine = StatikTemplateEngine(self)

            self.views = self.load_views()
            if len(self.views) == 0:
                raise NoViewsError("Project has no views configured")

            self.db = self.load_db_data(self.models)
            self.project_context = self.load_project_context()

            in_memory_result = self.process_views()

            if in_memory:
                result = in_memory_result
            else:
                # dump the in-memory output to files
                file_count = self.dump_in_memory_result(in_memory_result, output_path)
                logger.info('Wrote %d output file(s) to folder: %s' % (file_count, output_path))
                # copy any assets across, recursively
                self.copy_assets(output_path)
                result = file_count

        finally:
            try:
                # make sure to destroy the database engine (to provide for the possibility of database engine
                # reloads when watching for changes)
                self.db.shutdown()

            except Exception as e:
                logger.exception("Unable to clean up properly: %s" % e)

        return result

    def load_models(self):
        models_path = os.path.join(self.path, StatikProject.MODELS_DIR)
        logger.debug("Loading models from: %s" % models_path)
        if not os.path.isdir(models_path):
            raise MissingProjectFolderError(StatikProject.MODELS_DIR, "Project is missing its models folder")

        model_files = list_files(models_path, ['yml', 'yaml'])
        logger.debug("Found %d model(s) in project" % len(model_files))
        # get all of the models' names
        model_names = [extract_filename(model_file) for model_file in model_files]
        models = {}
        for model_file in model_files:
            model_name = extract_filename(model_file)
            models[model_name] = StatikModel(
                os.path.join(models_path, model_file),
                encoding=self.config.encoding,
                name=model_name,
                model_names=model_names
            )

        return models

    def load_views(self):
        """Loads the views for this project from the project directory
        structure."""
        view_path = os.path.join(self.path, StatikProject.VIEWS_DIR)
        logger.debug("Loading views from: %s" % view_path)
        if not os.path.isdir(view_path):
            raise MissingProjectFolderError(StatikProject.VIEWS_DIR, "Project is missing its views folder")

        view_files = list_files(view_path, ['yml', 'yaml'])
        logger.debug("Found %d view(s) in project" % len(view_files))
        views = {}
        for view_file in view_files:
            view_name = extract_filename(view_file)
            views[view_name] = StatikView(
                os.path.join(view_path, view_file),
                encoding=self.config.encoding,
                name=view_name,
                models=self.models,
                template_engine=self.template_engine
            )

        return views

    def load_db_data(self, models):
        data_path = os.path.join(self.path, StatikProject.DATA_DIR)
        logger.debug("Loading data from: %s" % data_path)
        if not os.path.isdir(data_path):
            raise MissingProjectFolderError(StatikProject.DATA_DIR, "Project is missing its data folder")

        return StatikDatabase(data_path, models, self.config.encoding, markdown_config=self.config.markdown_config)

    def load_project_context(self):
        """Loads the project context (static and dynamic) from the database/models for common use amongst
        the project's views."""
        # just make a copy of the project context
        context = copy(self.config.context_static)
        context['project_name'] = self.config.project_name
        context['base_path'] = self.config.base_path

        # now load the dynamic context
        context.update(self.load_project_dynamic_context())
        return context

    def load_project_dynamic_context(self):
        """Loads the dynamic context for this project, if any."""
        context = {}
        for varname, query in iteritems(self.config.context_dynamic):
            context[varname] = self.db.query(query)
        return context

    def process_views(self):
        """Processes the loaded views to generate the required output data."""
        output = {}
        logger.debug("Processing %d view(s)..." % len(self.views))
        for view_name, view in iteritems(self.views):
            # first update the view's context with the project context
            view.context.update(self.project_context)
            output = deep_merge_dict(output, view.process(self.db, safe_mode=self.safe_mode))
        return output

    def dump_in_memory_result(self, result, output_path):
        """Recursively dumps the result of our processing into files within the
        given output path.

        Args:
            result: The in-memory result of our processing.
            output_path: Full path to the folder into which to dump the files.

        Returns:
            The number of files generated (integer).
        """
        file_count = 0
        logger.debug("Dumping in-memory processing results to output folder: %s" % output_path)
        for k, v in iteritems(result):
            cur_output_path = os.path.join(output_path, k)

            if isinstance(v, dict):
                file_count += self.dump_in_memory_result(v, cur_output_path)
            else:
                if not os.path.isdir(output_path):
                    os.makedirs(output_path)

                filename = os.path.join(output_path, k)
                logger.info("Writing output file: %s" % filename)
                # dump the contents of the file
                with open(filename, 'wt', encoding=self.config.encoding) as f:
                    f.write(v)

                file_count += 1

        return file_count

    def copy_assets(self, output_path):
        """Copies all asset files from the source path to the destination
        path. If no such source path exists, no asset copying will be performed.
        """
        src_paths = []

        # if we have a theme
        if self.config.theme is not None:
            # assume it's in the folder: "themes/theme_name/assets"
            src_paths.append(os.path.join(
                self.path,
                StatikProject.THEMES_DIR,
                self.config.theme,
                StatikProject.ASSETS_DIR
            ))
            # NOTE: Adding the theme's assets directory *before* the project's internal assets directory
            #       always ensures that the project's own assets are copied *after* the theme's, thereby ensuring
            #       that the project's assets folder takes precedence over the theme's.

        # always attempt to copy from our base assets folder
        if os.path.isabs(self.config.assets_src_path):
            src_paths.append(self.config.assets_src_path)
        else:
            src_paths.append(os.path.join(self.path, self.config.assets_src_path))

        for src_path in src_paths:
            if os.path.exists(src_path) and os.path.isdir(src_path):
                dest_path = self.config.assets_dest_path
                if not os.path.isabs(dest_path):
                    dest_path = os.path.join(output_path, dest_path)

                logger.info("Copying assets from %s to %s..." % (src_path, dest_path))
                asset_count = copy_tree(src_path, dest_path)
                logger.info("Copied %s asset(s)" % asset_count)
            else:
                logger.info("Missing assets source path - skipping copying of assets: %s" % src_path)
