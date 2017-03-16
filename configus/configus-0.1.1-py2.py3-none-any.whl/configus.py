import os
import sys
import trafaret


DefaultEnvFile = '.env'


def config(schema, env=None, ignore_extra=True, config_file=DefaultEnvFile):

    assert isinstance(schema, trafaret.Trafaret), "Unexpected schema"

    env = env or os.environ.copy()
    if ignore_extra:
        schema = schema.ignore_extra('*')

    envfile = maybe_read_envfile(config_file)

    _env = envfile.copy()
    _env.update(**env)

    agrs_env = maybe_get_argv()
    _env.update(**agrs_env)

    return schema.check(_env)


def maybe_get_argv(argv=()):
    vars = {}
    argv = argv or sys.argv[1:]
    for arg in argv:
        # todo: make more posix compliant argv parsing
        parts = arg.split('=')
        if len(parts) != 2:
            continue
        key, val = parts[0], parts[1]
        key = key.strip('-')
        vars[key] = val
    return vars


def maybe_read_envfile(file_name):
    if not os.path.exists(file_name):
        if file_name == DefaultEnvFile or not file_name:
            return {}
        raise EnvironmentError('Passed envfile does not exists {}'.format(file_name))

    with open(file_name, 'r') as efile:
        content = efile.readlines()
    return parse_envfile(content)


def parse_envfile(lines):
    vars = {}
    for expression in lines:
        expression = expression.strip('\t\n ')
        if not expression:
            continue
        if expression.startswith('export'):
            expression = expression[6:]

        parts = expression.split('=')
        if len(parts) != 2:
            continue
        key, val = parts[0].strip(), parts[1].strip()
        if not key:
            continue
        vars[key] = val
    return vars
