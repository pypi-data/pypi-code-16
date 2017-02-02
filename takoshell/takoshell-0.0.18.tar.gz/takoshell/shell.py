# This file is part of tako
# Copyright (c) 2015-2017 Adam Hartz <hartz@mit.edu> and contributors
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the Soopycat License, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the Soopycat License for more details.
#
# You should have received a copy of the Soopycat License along with this
# program.  If not, see <https://smatz.net/soopycat>.
#
#
# tako is a fork of xonsh (http://xon.sh)
# xonsh is Copyright (c) 2015-2016 the xonsh developers and is licensed under
# the 2-Clause BSD license.

# -*- coding: utf-8 -*-
"""The tako shell"""
from takoshell.environ import takorc_context
from takoshell.execer import Execer


class Shell(object):
    """Main tako shell.

    Initializes execution environment.
    """

    def __init__(self, ctx=None, config=None, rc=None, **kwargs):
        """
        Parameters
        ----------
        ctx : Mapping, optional
            The execution context for the shell (e.g. the globals namespace).
            If none, this is computed by loading the rc files. If not None,
            this no additional context is computed and this is used
            directly.
        config : str, optional
            Path to configuration file.
        rc : list of str, optional
            Sequence of paths to run control files.
        """
        self.login = kwargs.get('login', True)
        self._init_environ(ctx, config, rc,
                           kwargs.get('scriptcache', True),
                           kwargs.get('cacheall', False))
        from takoshell.readline_shell import ReadlineShell
        self.shell = ReadlineShell(execer=self.execer,
                                   ctx=self.ctx, **kwargs)

    def __getattr__(self, attr):
        """Delegates calls to appropriate shell instance."""
        return getattr(self.shell, attr)

    def _init_environ(self, ctx, config, rc, scriptcache, cacheall):
        self.ctx = {} if ctx is None else ctx
        self.execer = Execer(config=config, login=self.login, tako_ctx=self.ctx)
        self.execer.scriptcache = scriptcache
        self.execer.cacheall = cacheall
        if self.login:
            # load run control files
            self.ctx.update(takorc_context(rcfile='/etc/takorc', absolute=True, execer=self.execer, initial=self.ctx))
            self.ctx.update(takorc_context(rcfile='preload.tako', execer=self.execer, initial=self.ctx))
        self.ctx['__name__'] = '__main__'
