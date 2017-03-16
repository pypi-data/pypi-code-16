import numpy
from collections import defaultdict


def analyze(file_path):
    data_map = defaultdict(list)
    with open(file_path, 'r') as f:
        for line in f:
            tokens = line.split(",")
            function = "%s.%s" % (tokens[1], tokens[2])
            execution_time = float(tokens[3])

            data_map.setdefault(function, []).append(execution_time)

    result = []
    for f, v in data_map.items():
        result.append((f, numpy.mean(v), numpy.percentile(v, 99.0), numpy.percentile(v, 95),))

    print("Function, Mean, 99.0th %ile, 99.5th %ile")
    for e in sorted(result, key=lambda x: x[2], reverse=True):
        print(e)
