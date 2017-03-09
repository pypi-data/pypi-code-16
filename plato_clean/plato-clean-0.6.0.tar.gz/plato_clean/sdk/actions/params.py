

def filter_ids(payload, ids_key, ids):
    if ids:
        payload[ids_key] = ids
    return payload


def filter_status(payload, status):
    if status:
        payload['status'] = status
    return payload


def filter_search_word(payload, search_word):
    if search_word:
        payload['searchWord'] = search_word
    return payload


def filter_limit(payload, limit):
    if limit:
        payload['limit'] = limit
    return payload


def filter_offset(payload, offset):
    if offset:
        payload['offset'] = offset
    return payload


def filter_reverse(payload, reverse):
    if reverse is not None:
        payload['reverse'] = reverse
    return payload


def filter_verbose(payload, verbose):
    if verbose is not None:
        payload['verbose'] = verbose
    return payload
