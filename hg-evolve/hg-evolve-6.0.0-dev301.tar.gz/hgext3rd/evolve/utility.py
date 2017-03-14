# Various utility function for the evolve extension
#
# Copyright 2017 Pierre-Yves David <pierre-yves.david@ens-lyon.org>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
from mercurial import node

def obsexcmsg(ui, message, important=False):
    verbose = ui.configbool('experimental', 'verbose-obsolescence-exchange',
                            False)
    if verbose:
        message = 'OBSEXC: ' + message
    if important or verbose:
        ui.status(message)

def obsexcprg(ui, *args, **kwargs):
    topic = 'obsmarkers exchange'
    if ui.configbool('experimental', 'verbose-obsolescence-exchange', False):
        topic = 'OBSEXC'
    ui.progress(topic, *args, **kwargs)

_depthcache = {}
def depth(repo, rev):
    cl = repo.changelog
    n = cl.node(rev)
    revdepth = _depthcache.get(n, None)
    if revdepth is None:
        p1, p2 = cl.parentrevs(rev)
        if p1 == node.nullrev:
            revdepth = 1
        elif p2 == node.nullrev:
            revdepth = depth(repo, p1) + 1
        else:
            ancs = cl.commonancestorsheads(cl.node(p1), cl.node(p2))
            depth_p1 = depth(repo, p1)
            depth_p2 = depth(repo, p2)
            if not ancs:
                revdepth = depth_p1 + depth_p2 + 1
            elif len(ancs) == 1:
                anc = cl.rev(ancs[0])
                revdepth = depth_anc = depth(repo, anc)
                revdepth += depth_p1 - depth_anc
                revdepth += depth_p2 - depth_anc
                revdepth += 1
            else:
                # multiple ancestors, we pick the highest and search all missing bits
                anc = max(cl.rev(a) for a in ancs)
                revdepth = depth(repo, anc)
                revdepth += len(cl.findmissingrevs(common=[anc], heads=[rev]))
        _depthcache[n] = revdepth
    # actual_depth = len(list(cl.ancestors([rev], inclusive=True)))
    # assert revdepth == actual_depth, (rev, revdepth, actual_depth)
    return revdepth
