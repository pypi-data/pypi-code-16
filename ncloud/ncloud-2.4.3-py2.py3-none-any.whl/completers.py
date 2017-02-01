from os import listdir, getcwd, path

import git

from ncloud.config import Config


LS_REMOTE_ARGS = '--tags --refs -q'
NEON_URL = 'https://github.com/NervanaSystems/neon'

# TODO: StatusCompleter


def fetch_tags(url):
    args = ' '.join((LS_REMOTE_ARGS, url))
    tags = git.cmd.Git().ls_remote(args.split()).split('\n')
    return [tag.split('/')[-1] for tag in tags]


def DatasetCompleter(prefix, **kwargs):
    from ncloud.commands.dataset import List as DatasetList  # noqa circular

    if prefix and not prefix.isdigit():
        return

    conf = Config()
    datasets = [
        str(dataset['id']) for dataset in DatasetList.call(conf)['datasets']
    ]
    return [dataset for dataset in datasets if dataset.startswith(prefix)]


def NeonVersionCompleter(prefix, **kwargs):
    if not prefix:
        return ['v1', 'v2']  # hack to autocomplete 'v'

    if not prefix.startswith('v'):
        return

    return [tag for tag in fetch_tags(NEON_URL) if tag.startswith(prefix)]


def HTTPCompleter(prefix, **kwargs):
    if 'http'.startswith(prefix):
        return ['http://', 'https://']
    if 'http://'.startswith(prefix):
        return ['http://']
    if 'https://'.startswith(prefix):
        return ['https://']
    return


def ModelCompleter(prefix, **kwargs):
    from ncloud.commands.model import List as ListModels  # noqa circular

    if prefix and not prefix.isdigit():
        return

    conf = Config()
    models = [str(model['id']) for model in ListModels.call(conf)['models']]
    return [model for model in models if model.startswith(prefix)]


def InteractiveSessionCompleter(prefix, **kwargs):
    from ncloud.commands.interact import List as ListSessions  # noqa circular

    if prefix and not prefix.isdigit():
        return

    conf = Config()
    sessions = [str(session['id']) for session in ListSessions.call(conf)]
    return [session for session in sessions if session.startswith(prefix)]


def BatchPredictionCompleter(prefix, **kwargs):
    from ncloud.commands.batch import List as ListBatch  # noqa circular

    if prefix and not prefix.isdigit():
        return

    conf = Config()
    sessions = [
        str(session['id']) for session in ListBatch.call(conf)['predictions']]
    return [session for session in sessions if session.startswith(prefix)]


def DirectoriesCompleter(prefix, **kwargs):
    # this exists because the built-in DirectoriesCompleter doesn't actually
    # work and is probably ghetto for windows users
    target_dir = path.dirname(prefix)
    try:
        names = listdir(target_dir or getcwd())
    except:
        return

    incomplete = path.basename(prefix)
    for name in names:
        if not name.startswith(incomplete):
            continue
        candidate = path.join(target_dir, name, '')  # '' to add trailing slash
        if path.isdir(candidate):
            yield candidate
