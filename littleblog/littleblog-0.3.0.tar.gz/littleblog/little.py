import os
from operator import attrgetter
import datetime
import shutil

import importlib.util

from jinja2 import Environment, FileSystemLoader

import markdown


md_extensions = [
    'fenced_code',
    'codehilite(linenums=True)',
]


class SettingsNotFound(Exception):
    pass


class Blog:

    def __init__(self, name, title=None):
        self._load_settings(name)
        self.title = title or name

    def __str__(self):
        return self.title

    def __repr__(self):
        return self.__str__()

    def _load_settings(self, name):
        """ Load the settings.py file from the specified project_name directory """
        spec = importlib.util.spec_from_file_location(
            'settings', os.path.join(name, 'settings.py'))

        settings = importlib.util.module_from_spec(spec)

        try:
            spec.loader.exec_module(settings)
        except FileNotFoundError:
            raise SettingsNotFound(
                "Couldin't find settings for '{}'".format(name))

        settings.CONTENT_DIR = os.path.join(name, settings.CONTENT_DIR)
        settings.OUTPUT_DIR = os.path.join(name, settings.OUTPUT_DIR)
        settings.TEMPLATE_DIR = os.path.join(name, settings.TEMPLATE_DIR)
        settings.STATIC_DIR = os.path.join(name, settings.STATIC_DIR)

        self.settings = settings

    def _clear_old(self):
        """Remove old content from output and static directories"""
        # Remove the previously generated content
        shutil.rmtree(self.settings.OUTPUT_DIR, ignore_errors=True)

    def _copy_static(self):
        """Copy the contents of static to the output directory"""

        from_dir = self.settings.STATIC_DIR
        to_dir = os.path.join(
            self.settings.OUTPUT_DIR,
            os.path.basename(self.settings.STATIC_DIR)
        )

        shutil.copytree(from_dir, to_dir)

    def _populate_posts(self):
        """Clear the posts attribute and repopulate it with published posts"""
        self._posts = []

        for cur_dir, sub_dirs, files in os.walk(self.settings.CONTENT_DIR):
            for f in files:
                filepath = os.path.join(cur_dir, f)
                p = Post(self, filepath)
                if p.published and p.published <= datetime.datetime.now():
                    self._posts.append(p)

    @property
    def posts(self):
        try:
            return sorted(
                self._posts, key=attrgetter('published'), reverse=True)
        except AttributeError:
            return

    def _render_index(self):
        env = Environment(loader=FileSystemLoader(self.settings.TEMPLATE_DIR))
        template = env.get_template('list.html')
        return template.render(posts=self.posts)

    def render(self):
        """Render the contents of the output directory"""
        self._clear_old()
        # Create the new output dir
        os.makedirs(self.settings.OUTPUT_DIR, exist_ok=True)
        self._copy_static()
        self._populate_posts()
        # Write the detail page
        for p in self.posts:
            p.write()
        # Write the main index
        with open(os.path.join(self.settings.OUTPUT_DIR, 'index.html'), 'w') as out:
            out.write(self._render_index())


class Post:

    def __init__(self, blog, filepath):
        self.blog = blog
        self.filepath = filepath

    def __str__(self):
        return self.title or 'Untitled'

    def __repr__(self):
        return self.__str__()

    @property
    def content(self):
        """Returns the full unrendered content of the post"""
        with open(self.filepath) as f:
            return f.read()

    @property
    def title(self):
        """Returns the first H1 found in the page"""
        for line in self.content.split("\n"):
            if line.strip().startswith("# "):
                return line.lstrip("#").strip()

    @property
    def published(self):
        with open(self.filepath) as f:
            try:
                return datetime.datetime.strptime(
                    f.readline().strip(), "%Y-%m-%dT%H:%M")
            except ValueError:
                return

    @property
    def _outdir(self):
        content = self.blog.settings.CONTENT_DIR
        output = self.blog.settings.OUTPUT_DIR
        return os.path.dirname(self.filepath.replace(content, output, 1))

    @property
    def _outpath(self):
        fn = os.path.basename(self.filepath)
        return os.path.join(
            self._outdir,
            os.path.splitext(fn)[0] + ".html"
        )

    @property
    def url(self):
        return self._outpath.replace(self.blog.settings.OUTPUT_DIR, '', 1)

    @property
    def path(self):
        return self.url

    @property
    def html(self):
        """Returns the markdown rendered self.content"""
        content = "\n".join(self.content.split("\n")[1:])
        return markdown.markdown(content, extensions=md_extensions)

    def render_detail(self):
        settings = self.blog.settings
        env = Environment(loader=FileSystemLoader(settings.TEMPLATE_DIR))
        template = env.get_template('detail.html')
        return template.render(content=self.html, page_title=self.title)

    def write(self):
        os.makedirs(self._outdir, exist_ok=True)
        with open(self._outpath, 'w') as out:
            out.write(self.render_detail())
