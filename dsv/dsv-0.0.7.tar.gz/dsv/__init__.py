""" You can kind of see this as the scope of `dsv` when you 'import dsv'
The following functions become available:
dsv.__project__
dsv.__version__
dsv.run
dsv.print_version
"""
import json
from collections import Counter
import types
import csv

__project__ = "dsv"
__version__ = "0.0.7"

DELIMS = [",", "\t", ";", " ", "|", ":"]


def take(csvfile, n=100):
    lines = []
    for i, line in enumerate(csvfile):
        if i == n:
            break
        lines.append(line)
    return lines


def has_quotes(test_lines):
    counts = [x.count('"') for x in test_lines]
    if all([x > 0 for x in counts]):
        if all([x % 2 == 0 for x in counts]):
            return True
        else:
            return ValueError("Unbalanced quotes")  # pragma: no cover
    return False


def detect_problem_lines(lines, dialect):
    problem_lines = []
    for num, line in enumerate(lines):
        if line.count(dialect["delimiter"]) != dialect["num_cols"]:
            problem_lines.append(num)
    if problem_lines:
        for num_line in problem_lines:
            msg = "problem_lines (only looking at line < 100):\n"
            msg += "{}: '{}'\n".format(num_line, lines[num_line].strip())
        msg += "Using dialect:\n{}".format(json.dumps(dialect, indent=4))
        raise ValueError(msg.strip())


def add_delimiter(lines, dialect):
    c = Counter()
    dialect["test_n"] = min(len(lines), 10)
    for line in lines[-dialect["test_n"]:]:
        for delim in DELIMS:
            c[delim] += line.count(delim)
    pos = 1000
    for p, delim in enumerate(DELIMS):
        ncols = c[delim] // dialect["test_n"]
        rounded = c[delim] % dialect["test_n"] == 0
        if c[delim] and rounded and ncols > dialect["num_cols"]:
            if p < pos:
                pos = p
                dialect["num_cols"] = ncols
                dialect["delimiter"] = delim


def sniff_dialect(fname):
    dialect = {"delimiter": None, "doublequote": False, "quotechar": '"',
               "quoting": csv.QUOTE_MINIMAL, "skipinitialspace": False,
               "fname": fname, "lineterminator": "\n", "num_cols": -1,
               "test_n": 10, "strict": False}
    with open(fname) as csvfile:
        lines = take(csvfile)
        dialect["newline"] = "\r\n" if any([x.endswith("\r\n") for x in lines]) else "\n"
        dialect["doublequote"] = any(['""' in x for x in lines])
        #dialect["quoting"] = has_quotes(lines)
        add_delimiter(lines, dialect)
        if dialect["delimiter"] is None:
            msg = "{}: cannot find equally occuring delimiter among lines".format(fname)
            raise ValueError(msg)
        detect_problem_lines(lines[:-dialect["test_n"]], dialect)
        # print(dialect)
        dialect = {k: dialect[k] for k in ["delimiter", "doublequote",
                                           "lineterminator", "quotechar", "quoting", "skipinitialspace", "strict"]}
        return dialect


def write_dict(obj, fname):
    header = set()
    for o in obj:
        for k in o.keys():
            header.add(k)
    header = sorted(header)
    delimiter = None
    for delim in DELIMS:
        if not any([any([delim in str(y) for y in line.values()]) for line in obj[-100:]]):
            delimiter = delim
            break
    with open(fname, "w") as f:
        writer = csv.DictWriter(f, header, delimiter=delimiter)
        writer.writeheader()
        for row in obj:
            writer.writerow(row)


def write_list(obj, fname):
    delimiter = None
    for delim in DELIMS:
        if not any([delim in "".join(line) for line in obj[-100:]]):
            delimiter = delim
            break
    with open(fname, "w") as f:
        writer = csv.writer(f, delimiter=delimiter)
        for row in obj:
            writer.writerow(row)


def write(obj, fname):
    if isinstance(obj, (types.GeneratorType, str)):
        raise NotImplementedError  # pragma: no cover
    elif isinstance(obj[-1], dict):
        write_dict(obj, fname)
    elif isinstance(obj[-1], list):
        write_list(obj, fname)
    else:
        raise TypeError("No support for writing", type(obj[-1]))


def iread(fname):
    dialect = sniff_dialect(fname)
    csv.register_dialect("just.custom", **dialect)
    with open(fname) as csvfile:
        reader = csv.reader(csvfile, "just.custom")
        for line in reader:
            yield line


def read(fname):
    dialect = sniff_dialect(fname)
    csv.register_dialect("just.custom", **dialect)
    with open(fname) as csvfile:
        reader = csv.reader(csvfile, "just.custom")
        return list(reader)
