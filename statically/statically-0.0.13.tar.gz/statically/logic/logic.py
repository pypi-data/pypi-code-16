from statically.config import config

import requests, yaml, pathlib, jinja2, os, re

from markdown import Markdown
from markdown.extensions.codehilite import makeExtension as CodeHilite
from pyembed.markdown import PyEmbedMarkdown
from mdx_gfm import GithubFlavoredMarkdownExtension as Github

from functools import *

class Path(type(pathlib.Path())):
    pass

class Statically():

    children = ["content", "dist", "styles", "templates", "colorschemes"]

    def __init__(self, path):
        self.path = Path(os.path.abspath(path))

    def init(self):
        """Creates a new statically instance"""

        def fetch(path, url):
            """ Fetchs resources needed for statically: templates, styles, examples"""

            print("fetching: ", url)
            r = requests.get(url)
            with path.open("w") as file:
                file.write(r.content.decode('utf-8'))

        # yields lists of nested structures
        # > tfw black box programming
        def dict_generator(indict, pre=None):
            """ Generates lists with paths to a resource and its url"""
            pre = pre[:] if pre else []
            if isinstance(indict, dict):
                for key, value in indict.items():
                    if isinstance(value, dict):
                        for d in dict_generator(value, [key] + pre):
                            yield d
                    elif isinstance(value, list) or isinstance(value, tuple):
                        for v in value:
                            for d in dict_generator(v, [key] + pre):
                                yield d
                    else:
                        yield pre + [key, value]
            else:
                yield indict


        if self.path.is_dir():
            print("A statically instance already exists.")
            return

        # Create folder
        try:
            self.path.mkdir()
        except FileNotFoundError:
            print("Error: Can't create new Statically instance here")
            return

        for child in self.children:
            self.path.joinpath(child).mkdir()


        #config
        for resource in dict_generator(config.config):
            url = resource.pop()
            path = reduce(self.path.joinpath, resource+[""])
            fetch(path, url)


    def _read_config(self):
        """read the yaml config file"""
        with self.path.joinpath("config.yml").open() as f:
            cfg = yaml.load(f)
        return cfg['style'] + ".css", cfg['template'] + ".html", cfg['colorscheme'] + ".css"


    def update(self):
        """ Convert the markdown files to html """

        style, template, colorscheme = self._read_config()

        md = Markdown(extensions=[Github(), CodeHilite(), PyEmbedMarkdown()])
        t = self.path / Path("templates") / Path(template)
        jinja = jinja2.Template(t.open().read())


        def link(content, file):
            """Create valid links to files in statically instance"""
            def replacement(match):
                path = Path(unnest(file, 2)) / Path(match.group(2))

                return "[{0}]({1})".format(match.group(1), str(path))

            return re.sub(r'#\[(.*?)\]\((.*?)\)', replacement, content)

        def compile (content):
            return md.convert(content)

        def template(content, title, style, colorscheme):
            return jinja.render(title = title,
                                style = style,
                                colorscheme = colorscheme,
                                body = content)

        def unnest(path, offset=1):
            """ Return the relative path to a file in another branch of the file system"""
            l = len((self.path / Path("content")).parts)
            length = len(path.parts) - l - offset

            if length < 0:
                return ""
            p = Path('..')
            for i in range(length):
                p = p.joinpath('..')

            return p


        for file in (self.path / Path("content")).rglob('*.md'):
            print(file)
            with file.open() as f:
                content = file.open().read()

            content = link(content, file)

            html = template(compile(content),
                            file.stem,
                            unnest(file) / Path("styles") / Path(style),
                            unnest(file) / Path("colorschemes") / Path(colorscheme))

            target = self.path / Path("dist") / file.relative_to(self.path / Path("content"))

            if not target.parent.exists():
                target.parent.mkdir()

            print("Creating: ", str(target)[:-3])
            open(str(target)[:-3] + ".html", 'w').write(html)
