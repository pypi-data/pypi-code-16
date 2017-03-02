# -*- coding: iso-8859-1 -*-
#
# Copyright (C) 2011-2012 Edgewall Software
# All rights reserved.
#
# This software may be used and distributed according to the terms
# of the GNU General Public License, incorporated herein by reference.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://trac.edgewall.org/log/.


"""
Mercurial hook calling `trac-admin $ENV changeset added` for newly added
changesets

The Trac environments to be notified are configured in the `[trac]` section
of `hgrc`. The path to an environment is specified in the `env` key. More
environments can be specified by adding a suffix separated by a dot.

The path to the `trac-admin` executable can be specified in the `trac-admin`
key. A specific path can be set for each environment, by adding the same
suffix to the `trac-admin` key.

The maximum number of changesets to pass per call to `trac-admin` can be
configured with the `revs_per_call` key. The default is relatively low (80
on Windows, 500 on other systems) for maximum compatibility, and can be
increased if you often push thousands of changesets and the system supports
it.

If the `trac-admin` option is left empty, the hook opens the Trac environment
and calls the relevant Trac hook directly in the same process. This will only
work if Trac can be imported by the Python interpreter running Mercurial (e.g.
if both are installed globally). Note that this may result in increased memory
usage if Mercurial is executed as a long-running process (e.g. hgweb in WSGI
mode). In this last case, the option `cache_env` can be set to `true` to
cache the Trac environments across invocations, therefore avoiding the
environment setup time on each invocation.

If the Mercurial plugin is installed globally (i.e. not in one of Trac's
plugins directories), the hooks can be configured as follows:
{{{
[hooks]
commit = python:tracext.hg.hooks.add_changesets
changegroup = python:tracext.hg.hooks.add_changesets
}}}

Otherwise, place this file somewhere accessible, and configure the hooks as
follows:
{{{
[hooks]
commit = python:/path/to/hooks.py:add_changesets
changegroup = python:/path/to/hooks.py:add_changesets
}}}

A typical configuration for three environments looks like this:
{{{
[trac]
; For a single Trac environment
env = /path/to/env
trac-admin = /path/to/trac-admin

; Two more environments, with a specific trac-admin for the second
env.other = /path/to/other/env
env.third = /path/to/third/env
trac-admin.third = /path/to/third/trac-admin
}}}
"""

import os.path
import subprocess

close_fds = os.name == 'posix'


def expand_path(path):
    """Expand user references and environment variables in a path."""
    return os.path.expanduser(os.path.expandvars(path))


def add_changesets(ui, repo, node, **kwargs):
    """Commit hook calling `trac-admin $ENV changeset added $REPO $NODE ...`
    on all configured Trac environments, for all newly added changesets.
    """
    revs = range(repo[node].rev(), len(repo))
    error = False
    for name, env in ui.configitems('trac'):
        p = name.split('.', 1)
        if p[0] != 'env' or not env:
            continue
        env = expand_path(env)

        trac_admin = ui.config('trac', 'trac-admin', '')
        if len(p) > 1:
            trac_admin = ui.config('trac', 'trac-admin.' + p[1], trac_admin)

        if not trac_admin:
            cache_env = ui.configbool('trac', 'cache_env')
            from trac.env import open_environment
            from trac.versioncontrol.api import RepositoryManager
            env = open_environment(env, use_cache=cache_env)
            RepositoryManager(env).notify('changeset_added', repo.root, revs)
            continue

        try:
            revs_per_call = int(ui.config('trac', 'revs_per_call'))
        except (TypeError, ValueError):
            revs_per_call = 160 if os.name == 'nt' else 1000

        trac_admin = expand_path(trac_admin)
        for i in xrange(0, len(revs), revs_per_call):
            command = [trac_admin, env, 'changeset', 'added', repo.root]
            command.extend(str(r) for r in revs[i : i + revs_per_call])
            ui.debug("Calling %r\n" % (command,))
            proc = subprocess.Popen(command, close_fds=close_fds,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
            for line in proc.stdout:
                ui.write(line)
            proc.wait()
            if proc.returncode != 0:
                error = True
                ui.warn("trac-admin failed with return code %d for "
                        "environment:\n  %s\n" % (proc.returncode, env))
    return error
