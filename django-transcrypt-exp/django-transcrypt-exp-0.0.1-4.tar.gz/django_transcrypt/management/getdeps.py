import ast
import os
import glob
import site
from .imports import find_module
from .imports import NotAPackage
from org.transcrypt.utils import commandArgs


commandArgs.source = None


class ImportLister(ast.NodeVisitor):

    fileList = []
    moduleList = []

    def _process_names(self, names, module=None):
        for item in names:
            item_module = item.name
            if module is not None:
                item_module = module + "." + item_module
            self.moduleList.append(item_module)

    def find_modules(self, prefix=[]):
        """
        Returns a list of paths to dependencies
        """
        for pack in set(self.moduleList):
            path = None
            try:
                _, path, _ = find_module(pack)
            except (NotAPackage, ImportError):
                try:
                    _, path, _ = find_module(".".join(pack.split(".")[:-1]))
                except (NotAPackage, ImportError):
                    pass

            if path is not None:
                if os.path.isfile(path):
                    self.fileList.append(path)
                else:
                    self.fileList.append(path + "/*.py")

    def visit_Import(self, node):
        self._process_names(node.names)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        self._process_names(node.names, node.module)
        self.generic_visit(node)


def _get_filename_deps(filename):
    code = ""
    for file in glob.glob(filename):
        with open(file, encoding='utf-8') as f:
            code = f.read()
        tree = ast.parse(code)
        path = list(os.path.split(file)[:-1])
        importLister = ImportLister()
        importLister.generic_visit(tree)
        importLister.find_modules(path)

    return importLister.fileList


def getdeps(filename):
    # Initial run
    sitepackages_dir = site.getsitepackages()

    deps = set(_get_filename_deps(filename))
    deps_count = 0
    while deps_count != len(deps):
        deps_count = len(deps)
        for dep in deps:
            ndeps = _get_filename_deps(dep)
            for dir in sitepackages_dir:
                ndeps = [path for path in ndeps if not path.startswith(dir)]
            deps = deps | set(ndeps)

    return list(deps)
