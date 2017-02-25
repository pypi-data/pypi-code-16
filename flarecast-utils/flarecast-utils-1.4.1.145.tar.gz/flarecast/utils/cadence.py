def _time2timestamp(time):
    return time.hour * 3600 + time.minute * 60 + time.second


def _round2nextstep(timestamp):
    return int(
            round(float(timestamp) / _cadences[0]) * _cadences[0]
            ) % _sec_per_day


def datetime2cadence(dt):
    timestamp = _time2timestamp(dt.time())
    rounded = _round2nextstep(timestamp)
    return _cadence_timestamps[rounded]


_cadences = [
    12 * 60,
    1 * 3600,
    3 * 3600,
    6 * 3600,
    12 * 3600,
    24 * 3600,
]

cadence_names = [
    "12m",
    "1h",
    "3h",
    "6h",
    "12h",
    "24h",

]

_cadence_timestamps = {}
_sec_per_day = 24 * 3600

for _i, _cadence in enumerate(_cadences):
    for _step in range(_cadences[-1] / _cadence):
        _cadence_timestamps[_step * _cadence] = cadence_names[_i]
