__author__ = "David O'Gwynn"
__email__ = 'dogwynn@acm.org'
__version__ = '0.0.1'

import os
from pathlib import Path

import ruamel.yaml as _yaml
from ruamel.yaml.comments import CommentedMap
from gems import composite

def dump(*a, **kw) -> str:
    kw['Dumper'] = _yaml.RoundTripDumper
    kw['default_flow_style'] = False
    return _yaml.dump(*a, **kw)

def load(*a, **kw) -> CommentedMap:
    kw['Loader'] = _yaml.RoundTripLoader
    return _yaml.load(*a, **kw)
    
def read_yaml(path) -> CommentedMap:
    path = str(path) # for Path objects
    with open(path) as rfp:
        data = load(rfp)
    return data

def write_yaml(data, path) -> None:
    path = str(path) # for Path objects
    with open(path,'w') as wfp:
        dump(CommentedMap(data), wfp)

CREATE_HELP = '''\
To add tokens, specify them using YAML syntax:

service_a: 239e896bfe6f3b7705696c8cef84832e760b689a9633c454432fc407cb7a17af
service_b: 18c553b119e52cb7d1ab93699865dab38d02d09d13b453258edf859ec075d9d9
digitalocean:
  app1: a1e1c084540b51b33af3c6b63d48ede2937c8df92f7e6e3beb1f630ac750b851
  app2: 03593464105708646cc04d847ffc81c5b7775c462f68b573f2aff5d933635e17

To access them from Python:

>>> tokens = tokenmanager.get_tokens()
>>> tokens.service_a
'239e896bfe6f3b7705696c8cef84832e760b689a9633c454432fc407cb7a17af'
>>> tokens.digitalocean.app1
'a1e1c084540b51b33af3c6b63d48ede2937c8df92f7e6e3beb1f630ac750b851'

To use from bash:

$ python -m tokenmanager service_a
239e896bfe6f3b7705696c8cef84832e760b689a9633c454432fc407cb7a17af
$ python -m tokenmanager digitalocean.app1
a1e1c084540b51b33af3c6b63d48ede2937c8df92f7e6e3beb1f630ac750b851
'''

TOKEN_BP = '''\
# tokenmanager: Simple token manager for token-based REST APIs
# 
{help}
'''.format(
    help='\n'.join(
        '# '+l for l in CREATE_HELP.splitlines()
    )
)

TOKEN_FILENAME='.tokenmanager.yml'

def token_path() -> Path:
    return Path(os.environ['HOME'],TOKEN_FILENAME).expanduser().resolve()

def init_token_file(path=None) -> str:
    path = path or token_path()
    if path.exists():
        return False
    path.touch(mode=0o600)
    path.write_text(TOKEN_BP)
    return path

def get_tokens(path=None) -> composite:
    path = Path(path) if path else token_path()
    if not path.exists():
        path.write_text(TOKEN_BP)
        path.chmod(0o600)

    data = read_yaml(path) or {}
    return composite(data)

