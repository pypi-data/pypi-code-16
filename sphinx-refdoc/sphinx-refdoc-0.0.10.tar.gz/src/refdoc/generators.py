# -*- coding: utf-8 -*-
from __future__ import absolute_import
from os import makedirs
from os.path import dirname, exists, join

from . import rst
from .toctree import Toctree
from .util import get_packages, gen_ref_file_tree


def write_file(path, text):
    """ Write **text** to a file pointed by **path**.

    This will ensure that the parent directories for the file exist. If
    not, they will be created.
    """
    parent = dirname(path)
    if not exists(parent):
        makedirs(parent)

    with open(path, 'w') as fp:
        fp.write(text)


def gen_module_doc(fullname, toctree=None):
    """ Generate docfile for a given module.

    In principle the module docfile contains one automodule directive for that
    module + optional toctree if provided.

    :param str fullname:
        Full python name of the module.
    :param list<str> toctree:
        Inject this TOC tree into the module documentation.
    """
    doc_src = rst.title('``{}``'.format(fullname))

    if toctree is not None:
        doc_src += rst.section('Modules')
        doc_src += str(toctree)

    doc_src += rst.section("Reference")
    doc_src += rst.automodule(fullname)

    return doc_src


def gen_pkg_reference(pkg, dist_dir):
    """ Generate reference documentation for a given python package.

    :param Package pkg:
        The named tuple containing package metadata. This is one of the items
        returned by the call to :py:func:`get_packages`.
    :param str dist_dir:
        Destination directory.
    :return:
        Entry for the parent TOC (relative path without extension).
    """
    pkgdoc = pkg.fullname.replace('.', '_')
    pkgdoc_dir = join(dist_dir, pkgdoc)

    if not exists(pkgdoc_dir):
        makedirs(pkgdoc_dir)

    pkg_toc = Toctree()
    for module in pkg.modules:
        mod_name = pkg.fullname + '.' + module
        mod_path = join(pkgdoc_dir, module + '.rst')

        pkg_toc.add(module)
        write_file(mod_path, gen_module_doc(mod_name))

    index_file = join(pkgdoc_dir, 'index.rst')
    write_file(index_file, gen_module_doc(pkg.fullname, pkg_toc))

    pkg_index_file = join(pkgdoc, 'index')
    return pkg_index_file


def gen_reference_docs(src_dir, dst_dir):
    """ Generate sphinx source files for reference documentation and then.

    :param str src_dir:
        Path to the source code we want to generated reference for.
    :param str dst_dir:
        Where the resulting files will be stored. If the
    """
    pkgs = get_packages(src_dir)

    print("Generating reference documentation for:")
    print(gen_ref_file_tree(pkgs))

    main_toc = Toctree()
    for pkg in pkgs:
        pkg_index_file = gen_pkg_reference(pkg, dst_dir)
        main_toc.add(pkg_index_file)

    reference_index_content = '\n'.join([
        rst.title('Reference documentation'),
        rst.section('Packages'),
        str(main_toc)
    ])
    reference_index_file = join(dst_dir, 'index.rst')

    write_file(reference_index_file, reference_index_content)
