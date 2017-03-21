import re
from collections import Counter, defaultdict
from itertools import chain, islice
from operator import itemgetter
import numpy as np

"""
Author: Nikita Kazeev, kazeevn@yandex-team.ru
"""

camel_case_re = re.compile('.+?(?:(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z0-9])|$)')
TURBO_DISCARDED_TOKENS = {"Hlt2", "Decision"}


def camel_case_split(identifier):
    """
    This function is based on stackoverflow thread
    https://stackoverflow.com/questions/29916065/how-to-do-camelcase-split-in-python
    """
    matches = camel_case_re.finditer(identifier)
    return [m.group(0) for m in matches]


def get_core(data, discarded_tokens=TURBO_DISCARDED_TOKENS, cutoff=4):
    """
    The function splits the line names by CamelCaseParts, excludes discarded_tokens
    and merges cutoff most common tokens into a proposed stream name.
    The generated names are not necessary unique but are
    deterministic.

    Parameters
    ----------
    data : iterable
        Iterable of line names
    discarded_tokens : list of strings
        Tokens to be discarded from line names when generating stream name.
    cutoff : int
        Number of tokens used in the final name generation.
        See https://docs.python.org/2/library/itertools.html#itertools.islice
        for more details.
    Returns
    -------
    string
        Name of stream generated according to lines in stream.
    """

    tokens = Counter(chain(*map(camel_case_split, data)))
    return "".join(islice(filter(lambda token: token not in discarded_tokens,
                          map(itemgetter(0),
                              tokens.most_common())), cutoff))


def name_streams(streams_list):
    """
    Names the streams uniquely. Names are based on line names corresponding to this stream.

    Parameters
    ----------
    streams_list : list of lists [[<names of lines in stream one>], [...]]
        A list of streams as lists of line names.

    Returns
    -------
    list of strings
        List of names for the streams.
    """

    stream_names_cores = list(map(get_core, streams_list))
    cores_counts = Counter(stream_names_cores)
    unique_stream_names = []
    core_use_count = defaultdict(lambda: 1)
    for core_name in stream_names_cores:
        if core_use_count[core_name] == 1:
            unique_stream_names.append(core_name)
        else:
            unique_stream_names.append(r"%s_No%d" % (core_name, core_use_count[core_name]))
        core_use_count[core_name] += 1
    for idx, name in enumerate(unique_stream_names):
        unique_stream_names[idx] = str(name)
    return unique_stream_names


def get_named_streams(line_num_dict, line_stream_matrix, prescale):
    """
    Returns a dictionary with stream names as keys and lists of lines
    names being values.

    Parameters
    ----------
    line_num_dict : dict {<line name> : <line number>}
        Line name to line number mapping (number is used e.g. in event_line_matrix or line_stream_matrix)
    line_stream_matrix : numpy.ndarray of type bool
        Matrix that shows line-to-stream correspondence (True means line is included in stream).
    prescale : numpy.array of type float
        Array that contains prescale value for each line.

    Returns
    -------
    dict {'stream_name': {'lines': {<lines names>}, 'prescale': <prescale value>}
        Streaming scheme stored in fixed format. If prescales are present,
        <prescale value> = {<line name>: <line prescale value>}, otherwise
        it's set to None.
    """

    name_by_index = dict(map(reversed, line_num_dict.items()))
    for key, value in name_by_index.items():
        name_by_index[key] = str(value)
    streams_list = list(map(
        lambda stream: list(map(name_by_index.__getitem__, np.nonzero(stream)[0])),
        line_stream_matrix.T))
    
    streams_dict_list = []
    for streams_list_el in streams_list:
        nums = [line_num_dict[x] for x in streams_list_el]
        prescaled_lines_idx = list(set(nums) & set(np.arange(len(prescale))[prescale < 1]))
        if len(prescaled_lines_idx) > 0:
            prescale_dict = {name_by_index[x]: prescale[x] for x in prescaled_lines_idx}
            streams_dict_list.append({'lines': streams_list_el, 'prescaleVersion': 1, 'prescale':prescale_dict})
        else:
            streams_dict_list.append({'lines': streams_list_el, 'prescale': None})
    return dict(zip(name_streams(streams_list), streams_dict_list))
