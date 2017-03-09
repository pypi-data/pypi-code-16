def convert_into_key_value_format(jms_map):
    kv_dict = {}
    jms_entry = jms_map['map']['entry']
    if isinstance(jms_entry, dict):
        parse_jms_entry(jms_entry, kv_dict)
    else:
        parse_jms_entry_list(jms_entry, kv_dict)

    return kv_dict


def parse_jms_entry_list(entries, payload):
    for entry in entries:
        parse_jms_entry(entry, payload)


def parse_jms_entry(jms_entry, payload):
    jms_entry_string_value = jms_entry['string']
    if isinstance(jms_entry_string_value, list):
        key, value = jms_entry_string_value
    else:
        del jms_entry['string']
        key = jms_entry_string_value
        (value,) = jms_entry.values()
    payload[key] = value


def convert_jms_to_python(body, transformation):
    if isinstance(body, dict) and transformation == 'jms-map-json':
        return convert_into_key_value_format(body)
    else:
        return body
