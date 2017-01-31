from collections import defaultdict
import logging
import six
from six.moves import reduce


def select(records, keys):
    if not isinstance(keys, dict):
        keys = {k: k for k in keys}
    return map(lambda r: {keys[k]: v for (k, v) in six.iteritems(r) if k in keys},
               records)


def group(records, key):
    groups = defaultdict(list)
    try:
        for record in records:
            groups[record[key]].append(record)
    except KeyError:
        logging.error('Invalid record:\n{record}'.format(**locals()))
        raise
    return groups


def accumulate(records, keys):
    def add_next(s, n):
        for key in keys:
            s[key] += n.get(key, 0)
        return s
    return reduce(add_next, records, defaultdict(lambda: 0))


def statistic(records, group_key, accum_keys):
    stats = []
    groups = group(records, group_key)
    for group_name in groups:
        stat = accumulate(groups[group_name], accum_keys)
        stat[group_key] = group_name
        stats.append(stat)

    return sorted(stats, None, lambda x: x[group_key])


def join(t1, t2, on_keys):
    if isinstance(on_keys, str):
        on_keys = (on_keys, on_keys)

    def join_record(r1):
        (k1, k2) = on_keys
        try:
            r2 = next(r for r in t2 if r[k2] == r1[k1])
        except StopIteration:
            r2 = {}
        r = r1.copy()
        r.update(r2)
        return r

    return map(join_record, t1)
