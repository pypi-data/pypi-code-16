# -*- coding: utf-8 -*-

import logging
from pathlib import Path
from shutil import copyfile

from .decorators import reloadable
from .engine import WT


@reloadable('(re)loading configuration...')
def engine(fn):  # pragma: no cover
    return WT(fn)


def build(fn):  # pragma: no cover
    b = WT(fn, is_prod=True)
    try:
        b.build()
    except Exception as exc:
        logger = logging.getLogger('wt.build')
        logger.error('Error while building', exc_info=exc)
        return 1
    else:
        return 0


def init(path):
    src = Path(__file__).parent
    dst = Path(path)

    logger = logging.getLogger('wt.init')

    to_copy = (
        (['templates', 'wt.yaml'], ['wt.yaml']),
        (['templates', 'atom.xml'], ['templates', 'atom.xml']),
        (['templates', 'content.html'], ['templates', 'content.html']),
        (['templates', 'mainpage.html'], ['templates', 'mainpage.html']),
    )

    for left, right in to_copy:
        l = src.joinpath(*left)
        r = dst.joinpath(*right)
        if not l.exists():  # pragma: no cover
            logger.warn('[!] missing file "%s", skipping', str(l))
            continue
        if r.exists():  # pragma: no cover
            logger.warn('[!] target file "%s" exists, skipping', str(r))
            continue
        if not r.parent.exists():
            r.parent.mkdir(parents=True)
        copyfile(str(l), str(r))
        logger.info('[+] "%s" created', str(r))

    to_create = (
        (['content', 'pages', 'foo.md'], '# Foo page title\n[bar](/bar/)'),
        (['content', 'posts', 'bar.md'], '# Bar post title\n[baz](/baz/)'),
        (['content', 'posts', 'baz.md'], '# Baz post title\n[foo](/foo/)'),
        (['static', 'css', 'style.css'], '/*styles*/\nbody {color: coral}'),
    )
    for parts, text in to_create:
        p = dst.joinpath(*parts)
        if p.exists():  # pragma: no cover
            logger.warn('[!] target file "%s" exists, skipping', str(p))
            continue
        if not p.parent.exists():
            p.parent.mkdir(parents=True)
        p.write_text(text, encoding='utf-8')
        logger.info('[+] "%s" created', str(p))

    logger.info('[+] done')

    return 0
