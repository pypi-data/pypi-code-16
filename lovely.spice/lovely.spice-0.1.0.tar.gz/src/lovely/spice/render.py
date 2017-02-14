import sys
import os.path
import argparse
import logging
import shutil
from os.path import abspath, dirname, basename, realpath
from jinja2 import Environment, FileSystemLoader, StrictUndefined


logger = logging.getLogger(__name__)


def loadEnv(path):
    """ Load environment for given path
    """
    loader = FileSystemLoader(path, followlinks=True)
    return Environment(loader=loader, undefined=StrictUndefined)


class FolderRenderer(object):
    """ Render all templates to target

    The created files in target will have the same filename as the template so
    templatePath MUST NOT be the same as targetPath!
    """

    def __init__(self, templatePath, contextPath, targetPath):
        if (abspath(templatePath) == abspath(targetPath)):
            raise Exception("templatePath MUST NOT be targetPath")
        self.templatePath = templatePath
        self.targetPath = targetPath
        self.contextPath = contextPath

    def render(self):
        self._cleanupTarget()
        context = PyReader.loadFile(self.contextPath)
        env = loadEnv(self.templatePath)
        renderer = Renderer(env, context)
        for t in env.list_templates():
            path = realpath(os.path.join(self.targetPath, t))
            self._createContainingFolder(path)
            renderer.render(t, path)

    def _createContainingFolder(self, path):
        parent = dirname(path)
        if not os.path.exists(parent):
            logger.debug('creating folder %s', parent)
            os.makedirs(parent)

    def _cleanupTarget(self):
        if os.path.exists(self.targetPath):
            for subdir in os.listdir(self.targetPath):
                path = abspath(os.path.join(self.targetPath, subdir))
                logger.debug('removing folder %s', path)
                shutil.rmtree(path, True)


class FileRenderer(object):
    """ Render given template to target

    The given templateFile and targetFile MUST NOT be equal!
    """

    def __init__(self, templateFile, contextPath, targetFile):
        if (abspath(templateFile) == abspath(targetFile)):
            raise Exception("templateFile MUST NOT be targetFile")
        self.templateFile = templateFile
        self.templatePath = dirname(templateFile)
        self.targetFile = targetFile
        self.contextPath = contextPath

    def render(self):
        context = PyReader.loadFile(self.contextPath)
        env = loadEnv(self.templatePath)
        renderer = Renderer(env, context)
        t = env.get_template(basename(self.templateFile))
        renderer.render(t, self.targetFile)


class Renderer(object):

    def __init__(self, env, context):
        self.env = env
        self.context = context

    def render(self, tempPath, targetPath):
        template = self.env.get_template(tempPath)
        with file(targetPath, 'w+') as f:
            logger.debug('generating %s', targetPath)
            template.stream(self.context).dump(f, 'utf8')


class PyReader(object):

    @classmethod
    def loadFile(cls, path, l={}, g={}):
        absPath = abspath(path)
        with file(absPath, 'rb') as f:
            return cls.load(f)

    @classmethod
    def load(cls, f, l={}, g={}):
        sys.path.append(os.path.dirname(f.name))
        exec(f, g, l)
        if '__all__' in l:
            # only attributes listed in __all__ are allowed
            allowed = set(l['__all__'])
            for k in list(l.keys()):
                if k not in allowed:
                    del l[k]
        else:
            # remove all keys starting with _
            for k in list(l.keys()):
                if k.startswith('_'):
                    del l[k]
        return l


def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(
        description="Render templates with given context into target folder",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
    parser.add_argument(
        'template_path',
        help='The directory containing the templates to use.')
    parser.add_argument(
        'context_path',
        help='The path to the python file defining the context.')
    parser.add_argument(
        'target_path',
        help='The directory where the rendered files will be stored.')
    args = parser.parse_args()
    if os.path.isdir(args.template_path):
        renderCls = FolderRenderer
    else:
        renderCls = FileRenderer
    renderCls(
        args.template_path,
        args.context_path,
        args.target_path).render()
