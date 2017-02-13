# Decision tree operators
_OPERATORS = {
    "continuous.equal": lambda context, value: context == value,
    "enum.equal": lambda context, value: context == value,
    "continuous.greaterthan": lambda context, value: context > value,
    "continuous.greaterthanorequal": lambda context, value: context >= value,
    "continuous.lessthan": lambda context, value: context < value,
    "continuous.lessthanorequal": lambda context, value: context <= value,
    "interval.in": lambda context, value: context>=value["interval"]["from_included"] and context<value["interval"]["to_excluded"] if value["interval"]["from_included"] < value["interval"]["to_excluded"] else context>=value["interval"]["from_included"] or context<value["interval"]["to_excluded"],
}