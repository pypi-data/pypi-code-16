from tornado.web import HTTPError


def select_columns(resource, columns):
    return resource + '(' + ','.join(columns) + ')' if columns else ''


def unwrap_items(response):
    try:
        result   = response['response']['result']

        # Dont know the resource name but should be the only key
        assert len(result) == 1
        resource = list(result.values())[0]

        # wrap single resource results in array
        rows  = resource['row']
        items = rows if isinstance(rows, list) else [rows]

        items = [translate_item(i) for i in items]
        return items
    except (AssertionError, KeyError):
        unwrap_error(response)


def unwrap_error(zoho_error):
    try:
        response   = zoho_error['response']
        filtered   = {key: value for key, value in response.items() if key.lower() != 'uri'}  # noqa

        # Dont know the error name but should ony be one key left
        assert len(filtered) == 1
        _, error      = filtered.popitem()
        code, message = error['code'], error['message']

        status_code = http_status_code(zoho_code=code)
        raise HTTPError(status_code, reason=message)
    except (AssertionError, KeyError, IndexError):
        raise ValueError("Couldn't parse zoho result")


def http_status_code(*, zoho_code):  # pragma: no cover
    zoho_code = str(zoho_code)

    if zoho_code in ["4832"]:
        return 404  # not found
    else:
        return 500  # internal server error


def translate_item(item):
    fields = item.get('fl', item.get('FL'))
    fields = fields if isinstance(fields, list) else [fields]

    def nullify(value):
        return None if value == 'null' else value

    return {kwarg['val']: nullify(kwarg['content']) for kwarg in fields}
