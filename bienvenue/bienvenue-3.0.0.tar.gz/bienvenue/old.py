

    return (_envb(d, key, default) if isinstance(default, bool) else
            _envi(d, key, default) if isinstance(default, int) else
            _envj(d, key, default) if isinstance(default, (list, dict)) else
            _envs(d, key, default))




def _envs(d, key, default):
    return d.get(key, default)


def _envb(d, key, default):
    value = d.get(key)
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, string_types):
        v = value.lower()
        if v in ['1', 'on', 't', 'true', 'y', 'yes']:
            return True
        if v in ['0', 'off', 'f', 'false', 'n', 'no']:
            return False
    logger.warning('%s bool value is invalid (%r)', key, value)
    return default


def _envi(d, key, default):
    value = d.get(key)
    if value is None:
        return default
    if isinstance(value, int):
        return value
    if isinstance(value, string_types):
        try:
            return int(value)
        except ValueError:
            pass
    logger.warning('%s int value is invalid (%r)', key, value)
    return default


def _envj(d, key, default):
    value = d.get(key)
    if value is None:
        return default
    if isinstance(value, string_types):
        try:
            return json.loads(value)
        except json.JSONDecodeError as e:
            logger.warning('%s JSON value is %r, %s: %s', key, value,
                           e.__class__.__name__, e)
    return default
