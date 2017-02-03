import datetime


ZERO = datetime.timedelta(0)


class UTC(datetime.tzinfo):
    """UTC"""

    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return ZERO

utc = UTC()


def parse_date(value):
    """Parses a string and returns a time zone-aware datetime instance.

    If the value is an invalid format the original value is returned.

    >>> parse_date('2016-01-02T03:04:05Z')
    datetime.datetime(2016, 1, 2, 3, 4, 5, tzinfo=<codebase.utils.UTC ...>) # doctest: +ELLIPSIS
    >>> parse_date('foo')
    'foo'
    >>> parse_date(None)
    >>>
    """
    # Codebase uses 1 format: 2016-12-14T14:35:20Z
    dt_format = '%Y-%m-%dT%H:%M:%SZ'

    try:
        dt = datetime.datetime.strptime(value, dt_format)
    except (TypeError, ValueError):
        return value
    else:
        dt = dt.replace(tzinfo=utc)

        return dt


def format_since_dt(value):
    """Converts a datetime to UTC and returns a string to use with the activity
    feed's `since` keyword argument.
    """
    # Actually the API seems to parse dates too.

    try:
        value = value.astimezone(utc)
    except ValueError:
        # Naive datetime, we assume it is meant for UTC.
        value = value.replace(tzinfo=utc)

    # '2014-09-26 17:26:47 +0000'
    result = value.strftime('%Y-%m-%d %H:%M:%S +0000')

    return result


def build_create_note_payload(assignee_id=None, category_id=None, content=None,
        milestone_id=None, priority_id=None, private=None, status_id=None,
        summary=None, time_added=None, upload_tokens=None):
    """Returns a dict to use when creating a ticket note (or for changing a
    ticket's properties).
    """
    payload = {
        'content': content,
        'private': private,
        'time_added': time_added,
        'upload_tokens': upload_tokens,

    }

    changes = {
        'assignee_id': assignee_id,
        'category_id': category_id,
        'milestone_id': milestone_id,
        'priority_id': priority_id,
        'status_id': status_id,
        'summary': summary,
    }

    # And then we remove any keys set to None.
    payload = {k: v for k, v in payload.items() if v is not None}
    changes = {k: v for k, v in changes.items() if v is not None}

    if changes:
        payload['changes'] = changes

    return payload


def quote_search_value(value):
    """Returns a status like 'In progress' as '"In progress"'."""
    value = str(value)
    value = value.replace("'", '')
    value = value.replace('"', '')
    value = u'"%s"' % value

    return value


def iterable(value):
    """True if value is iterable (except for strings)."""
    if isinstance(value, basestring):
        return False

    try:
        iter(value)
    except TypeError:
        return False
    else:
        return True


def build_ticket_search_query(**kwargs):
    """Returns a string for use in a ticket search query.

    Returns an empty string if there are no query parameters.
    """
    params = []

    # Order params, makes testing simpler.
    for key, value in sorted(kwargs.items()):
        if value is None:
            continue

        if not iterable(value):
            value = [value]

        value = ','.join(quote_search_value(v) for v in value)
        term = '%s:%s' % (key, value)
        params.append(term)

    query = ' '.join(params)

    return query


def encode_dict(d, encoding='UTF-8'):
    """Converts unicode and datetime values to encoded strings."""
    result = {}

    for k, v in d.items():
        if isinstance(v, unicode):
            v = v.encode(encoding)
        elif isinstance(v, datetime.datetime):
            v = str(v)

        result[k] = v

    return result
