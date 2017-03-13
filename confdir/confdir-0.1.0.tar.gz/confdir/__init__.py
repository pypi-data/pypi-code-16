import os
import json


def load_conf(path):
    try:
        if os.path.isdir(path):
            items = (
                (name, load_conf(os.path.join(path, name)))
                for name in sorted(os.listdir(path)) if not name.startswith('.')
            )
            if os.path.exists(os.path.join(path, '.list')):
                return list(item[1] for item in items)
            elif os.path.exists(os.path.join(path, '.set')):
                return set(item[1] for item in items)
            elif os.path.exists(os.path.join(path, '.tuple')):
                return tuple(item[1] for item in items)
            else:
                return dict(items)
        else:
            return json.load(open(path))
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(
            'Could not load settings from path "{}": {}'.format(path, e)
        )
