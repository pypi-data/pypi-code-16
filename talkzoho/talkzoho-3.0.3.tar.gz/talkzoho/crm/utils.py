import inflect

from datetime import date, datetime

from tornado.web import HTTPError

singular_noun = inflect.engine().singular_noun


def select_columns(resource, columns):
    return resource.lower() + '(' + ','.join(columns) + ')' if columns else ''


def to_zoho_value(value, *, key=None):
    cdata = '<![CDATA[{}]]>'

    if value is None:
        return ''
    elif key == 'Product Details' and isinstance(value, list):
        return format_rows(name='product', items=value)
    elif isinstance(value, list):
        return cdata.format(';'.join(value))
    elif isinstance(value, datetime) or isinstance(value, date):
        return cdata.format(value.strftime('%Y-%m-%d %H:%M:%S'))
    else:
        return cdata.format(value)


def record_to_xml_data(record: dict):
    lines = ['<FL val="{}">{}</FL>'.format(k, to_zoho_value(v, key=k)) for
             k, v in record.items()]

    return ''.join(lines)


def format_rows(*, name: str='row', items):
    if type(items) is not list:
        items = [items]

    rows = ['<{0} no="{1}">{2}</{0}>'.format(name, index + 1, record_to_xml_data(item))
            for index, item in enumerate(items)]

    return ''.join(rows)


def wrap_items(items, *, module_name: str):
    return '<{module_name}>{rows}</{module_name}>'.format(
        module_name=module_name,
        rows=''.join(format_rows(items=items)))


def unwrap_items(response):
    try:
        result = response['response']['result']

        if len(result) == 1:
            # Don't know the resource name but should be the only key
            resource = list(result.values())[0]
            rows     = resource['row']
        elif len(result) == 2:
            # On update message returns two keys message and record
            rows     = result['recorddetail']
        else:
            raise ValueError('Unexpected looking response.')

        return translate_items(rows)
    except (AssertionError, KeyError):
        return unwrap_error(response)


def unwrap_error(zoho_error):
    try:
        response   = zoho_error['response']
        filtered   = {key: value for key, value in response.items() if key.lower() != 'uri'}  # noqa

        # Dont know the error name but should ony be one key left
        assert len(filtered) == 1
        _, error      = filtered.popitem()
        code, message = error['code'], error['message']

        # codes returned on successful deletion of file/record
        if code in ['4800', '5000']:
            return True

        status_code = http_status_code(zoho_code=code)
        raise HTTPError(status_code, reason='{}: {}'.format(code, message))
    except (AssertionError, KeyError, IndexError):
        raise ValueError("Couldn't parse zoho result")


def http_status_code(*, zoho_code):  # pragma: no cover
    zoho_code = str(zoho_code)

    if zoho_code in ["4000", "4401", "4600", "4831", "4832", "4835", "4101", "4420"]:  # noqa
        return 400  # bad request
    elif zoho_code in ["4501", "4834"]:
        return 401  # unauthorised
    elif zoho_code in ["4502", "4890"]:
        return 402  # payment required
    elif zoho_code in ["4487", "4001", "401", "401.1", "401.2", "401.3"]:
        return 403  # forbidden
    elif zoho_code in ["4102", "4103", "4422"]:
        return 404  # not found
    elif zoho_code in []:
        return 405  # method not allowed
    elif zoho_code in ['4814']:
        return 409  # conflict
    elif zoho_code in ["4807"]:
        return 413  # payload too large
    elif zoho_code in ["4424"]:
        return 415  # payload too large
    elif zoho_code in ["4101", "4809"]:
        return 423  # locked
    elif zoho_code in ["4820", "4421", "4423"]:
        return 429  # too many requests
    else:
        return 500  # internal server error


def translate_items(rows):
    # wrap single resource results in array
    items = rows if isinstance(rows, list) else [rows]
    return [translate_item(i) for i in items]


def translate_item(item):
    fields = item.get('fl', item.get('FL'))
    fields = fields if isinstance(fields, list) else [fields]

    def nullify(value):
        return None if value == 'null' else value

    return {
        kwarg['val']: nullify(kwarg['content']) if 'content' in kwarg else translate_items(kwarg['product'])
        for kwarg in fields}


def make_module_id_name(module_map):
    if module_map.canonical_name.startswith('CustomModule'):
        return '{}_ID'.format(module_map.canonical_name.upper())
    else:
        return '{}ID'.format(singular_noun(module_map.canonical_name.upper()))
