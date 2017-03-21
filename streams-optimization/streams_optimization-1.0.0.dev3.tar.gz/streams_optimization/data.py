import os
import json
import gzip
import pickle
import re
import logging
import numpy as np
import scipy.sparse
import cast_unicode_to_str
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _gen_names_from_input_file_name(path_to_data_file):
    """
    Helper function that generates files' names (with path included) for event_line_matrix and line_num_dict.

    Parameters
    ----------
    path_to_data_file : string
        Path to data file of format ".json.gz" with HL2 decisions.

    Returns
    -------
    event_line_matrix_filename : string
        Name of file containing event_line_matrix for reading or writing purposes.
    line_num_dict_filename : string
        Name of file containing line_num_dict for reading or writing purposes.
    """
    dir_path = os.path.dirname(path_to_data_file)
    filename_prefix = os.path.basename(path_to_data_file).split(os.extsep)[0]
    event_line_matrix_filename = os.path.join(dir_path, ".".join([filename_prefix + "_event_line_matrix", "pcl"]))
    line_num_dict_filename = os.path.join(dir_path, ".".join([filename_prefix + "_line_num_dict", "json"]))
    return event_line_matrix_filename, line_num_dict_filename


def read_events_and_lines_from_raw(path_to_data_file, write_to_readable_format=True):
    """
    Translates HL2 decisions to scipy.sparse.dok_matrix and dictionary for further processing.

    Parameters
    ----------
    path_to_data_file : string
        Path to data file of format ".json.gz" with HL2 decisions. Way to generate this file is described
        at YSDA/ turbo_stream_streaming repository at gitlab: https://gitlab.cern.ch/YSDA/turbo_stream_streaming
    write_to_readable_format : bool
        If True, in the directory where data file is located will be created sparse_event_line_matrix and line_num_dict
        in ".pcl" and ".json" formats accordingly. The files can be used to reduce the reading time in future runs
        on the same dataset.
         !!! "sparse_event_line_matrix" is stored as scipy.sparse.dok_matrix to reduce disk space usage (casted to numpy array
         it takes 10 times more disk space).

    Returns
    -------
    sparse_event_line_matrix : scipy.sparse.dok_matrix of type bool
        Matrix that shows event-line correspondence.
    line_num_dict : dict {<line name> : <line number>}
        Line name to line number mapping (number is used e.g. in sparse_event_line_matrix or line_stream_matrix)
    """
    lines = set()
    input_file = gzip.GzipFile(path_to_data_file)
    for n_events, line in enumerate(input_file):
        event = json.loads(line.strip())
        lines.update([line_name.replace("Decision", "") for line_name in event['Hlt2Lines']])
    n_events += 1
    line_num_dict = dict(zip(lines, range(len(lines))))

    input_file.seek(0)
    sparse_event_line_matrix = scipy.sparse.dok_matrix((n_events, len(lines)), dtype=np.bool_)

    for index, text_line in enumerate(input_file):
        lines_in_event = json.loads(text_line)['Hlt2Lines']
        for line in lines_in_event:
            sparse_event_line_matrix[index, line_num_dict[line.replace("Decision", "")]] = True

    if write_to_readable_format:
        event_line_matrix_filename, line_num_dict_filename = _gen_names_from_input_file_name(path_to_data_file)
        with open(event_line_matrix_filename, 'w') as output_file:
            pickle.dump(sparse_event_line_matrix, output_file)
        with open(line_num_dict_filename, "w") as output_file:
            json.dump(line_num_dict, output_file)
    
    line_num_dict = cast_unicode_to_str.convert(line_num_dict)
    return sparse_event_line_matrix, line_num_dict


def read_scheme_from_defs(line_num_dict, path_to_streaming_scheme=None, stream_lines_dict=None):
    """
    Reads scheme from stream definitions in Tesla format to "numpy.ndarray" format and prescale values
     to dictionary. If path to streaming scheme is present, streams defenitions are read from file,
      otherwise passed dict is used.

    Parameters
    ----------
    path_to_streaming_scheme : string
        Path to ".json" file containing streaming scheme in format
        {'stream_name': {'lines': {<lines names>}, 'prescale': <prescale value>}. If prescales are present,
        <prescale value> = {<line name>: <line prescale value>}, otherwise it's set to None.
    line_num_dict : dict {<line name> : <line number>}
        Line name to line number mapping (number is used e.g. in event_line_matrix or line_stream_matrix)
    stream_lines_dict : {'stream_name': {'lines': {<lines names>}, 'prescale': <prescale value>}
        Dictionary with streams definitions and prescale values.

    Returns
    -------
    streaming_scheme : numpy.ndarray of type bool
        Matrix that shows line-to-stream correspondence (True means line is included in stream).
    stream_num_dict : dict {<stream name> : <stream number>}
        Stream name to stream number mapping (number is used e.g. in line_stream_matrix)
    prescale_dict : dict {<line name> : <prescale value>}
        Dict with prescale values for lines from streams definitions
    """
    if stream_lines_dict is None:
        if os.path.isfile(path_to_streaming_scheme):
            with open(path_to_streaming_scheme, 'r') as input_file:
                stream_lines_dict = json.load(input_file)
        else:
            raise ValueError('File with streams definitions not found!')
    n_lines = len(line_num_dict)
    streaming_scheme = np.zeros([n_lines, len(stream_lines_dict)], dtype=np.bool)
    stream_num_dict = {}
    prescale_dict = {}
    for stream_index, (stream_name, lines_set) in enumerate(stream_lines_dict.items()):
        for line_name in list(lines_set['lines']):
            if line_name in line_num_dict.keys():
                streaming_scheme[line_num_dict[line_name], stream_index] = True
            else:
                logging.info('Line not found in line_num_dict:', line_name)
        if lines_set['prescale'] is not None:
            prescale_dict.update(lines_set['prescale'])
        stream_num_dict[stream_name] = stream_index
    stream_num_dict = cast_unicode_to_str.convert(stream_num_dict)
    prescale_dict = cast_unicode_to_str.convert(prescale_dict)
    return streaming_scheme, stream_num_dict, prescale_dict


def read_modules_dict(line_num_dict, path_to_modules_definitions='', modules_definitions_dict=None):
    """
    Generates dictionary with mapping lines-to-modules split according to the input data.
    If path available, reads definitions from the file, otherwise uses provided dict.
    If module "ALL" with all line is present, it's discarded to avoid data duplication.

    Parameters
    ----------
    line_num_dict : dict {<line name> : <line number>}
        Line name to line number mapping (number is used e.g. in event_line_matrix or line_stream_matrix)
    path_to_modules_definitions : string
        Path to ".json" with modules definitions in format <module name> : <list of lines' names or regexp>
    modules_definitions_dict : dict {<module name> : <list of lines' names or regexp>
        Dictionary with modules definitions.

    Returns
    -------
    module_line_dict : dict {<module name> : <lines' names>}
        Module name to list of line names corresponding to this module mapping.
    """
    if os.path.isfile(path_to_modules_definitions):
        with open(path_to_modules_definitions, 'r') as input_file:
            module_line_name_dict = cast_unicode_to_str.json_load_byteified(input_file)
    elif modules_definitions_dict is not None:
        module_line_name_dict = modules_definitions_dict
    else:
        raise ValueError('Modules definitions are not found!')

    line_was_used = np.zeros(len(line_num_dict), dtype=bool)

    if 'ALL' in module_line_name_dict.keys():
        module_line_name_dict.pop('ALL')
    line_module_dict = {}
    for line_name, line_index in line_num_dict.items():
        for module_name, list_of_regexps in module_line_name_dict.items():
            for regexp in list_of_regexps:
                if re.match(regexp, line_name):
                    if line_was_used[line_index]:
                        raise ValueError('Line matches more than one module regexp.')
                    line_was_used[line_index] = True
                    line_module_dict[line_name] = module_name
                    break

    module_line_dict = defaultdict(list)
    for line_name, module_name in line_module_dict.items():
        module_line_dict[module_name].append(line_name)
    module_line_dict = cast_unicode_to_str.convert(module_line_dict)
    return module_line_dict


def drop_unused_lines(event_line_matrix, line_num_dict, scheme, path_to_streaming_scheme='', stream_lines_dict=None):
    """
    Drops from data (event_line_matrix and line_num_dict) lines that are absent in provided scheme.
    Then reloads the scheme according to the path.
    Usually this function is used to work only with lines active in baseline.

    Parameters
    ----------
    event_line_matrix : numpy.ndarray of type bool
        Matrix that shows event-line correspondence.
    line_num_dict : dict {<line name> : <line number>}
        Line name to line number mapping (number is used e.g. in event_line_matrix or line_stream_matrix)
    scheme : numpy.ndarray of type bool
        Matrix that shows line-to-stream correspondence (True means line is included in stream) in selected streams
        definitions.
    path_to_streaming_scheme : string
        Path to ".json" file containing streaming scheme in format
        {'stream_name': {'lines': {<lines names>}, 'prescale': <prescale value>}. If prescales are present,
        <prescale value> = {<line name>: <line prescale value>}, otherwise it's set to None.
    stream_lines_dict : {'stream_name': {'lines': {<lines names>}, 'prescale': <prescale value>}
        Dictionary with streams definitions and prescale values.

    Returns
    -------
    event_line_matrix : numpy.ndarray of type bool
        Matrix that shows event-line correspondence.
    line_num_dict : dict {<line name> : <line number>}
        Line name to line number mapping (number is used e.g. in event_line_matrix or line_stream_matrix)
    scheme : numpy.ndarray of type bool
        Matrix that shows line-to-stream correspondence (True means line is included in stream) in selected streams
        definitions.
    stream_num_dict : dict {<stream name> : <stream number>}
        Stream name to stream number mapping (number is used e.g. in line_stream_matrix)
    """
    nonactive_lines_list = []
    for i in range(scheme.shape[0]):
        if sum(scheme[i, :]) == 0:
            nonactive_lines_list.append(i)
    inv_line_num_dict = {num: name for name, num in line_num_dict.items()}
    active_lines = list(set(range(event_line_matrix.shape[1])) - set(nonactive_lines_list))
    
    for key in nonactive_lines_list:
        inv_line_num_dict.pop(key)

    inv_line_num_dict_new = dict(enumerate(inv_line_num_dict.values()))
    indices_new_order = [line_num_dict[elem[1]] for elem in sorted(inv_line_num_dict_new.items(), key=lambda (k, v): k)]

    event_line_matrix_new = event_line_matrix[:, indices_new_order]
    line_num_dict_new = {name: num for num, name in inv_line_num_dict_new.items()}

    for i in range(len(active_lines)):
        if inv_line_num_dict[active_lines[i]] != inv_line_num_dict_new[i]:
            raise ValueError('Failed to drop lines that are inactive in baseline.')

    event_line_matrix = event_line_matrix_new
    line_num_dict = line_num_dict_new
    scheme, stream_num_dict, _ = read_scheme_from_defs(line_num_dict, path_to_streaming_scheme, stream_lines_dict)
    return [event_line_matrix,
            line_num_dict,
            scheme,
            stream_num_dict]


def _get_lines_active_events(event_line_matrix, lines_num):
    """
    Helper function, returns numbers of events active in selected lines

    Parameters
    ----------
    event_line_matrix : numpy.ndarray of type bool
        Matrix that shows event-line correspondence.
    lines_num : list of unsigned ints
        List with numbers of lines to check.
    Returns
    -------
    list of ints
        List with numbers of events active in selected lines.
    """
    active_events = event_line_matrix[:, lines_num].sum(axis=1).nonzero()[0]
    return active_events


def add_submodules_and_extra_modules(line_num_dict,
                                     module_line_dict,
                                     additional_modules_dict=None,
                                     submodules_dict=None):
    """
    This function allows to add extra modules to an existing module_line_dict or split its modules into
    submodules if necessary. If all module's lines are moved to submodules, it's erased, otherwise it stays with
    lines not included in any submodule.

    Parameters
    ----------
     line_num_dict : dict {<line name> : <line number>}
        Line name to line number mapping (number is used e.g. in event_line_matrix or line_stream_matrix)
    module_line_dict : dict {<module name> : <lines' names>}
        Module name to list of line names corresponding to this module mapping.
    additional_modules_dict : dict {<module_name>: <lines' names>}
        Additional modules for the existing module_line_dict.
    submodules_dict : dict {<module name> : dict {<submodule name>: <lines' names>}}
        Dictionary that shows into which parts should be divided specified modules. Every entry shows into which
        submodules current module's lines should be moved.

    Returns
    -------
    module_line_dict : dict {<module name> : <lines' names>}
        Modified module name to list of line names corresponding to this module mapping.
    """

    if additional_modules_dict is not None:
        if module_line_dict is None:
            module_line_dict = {}
        for module_name, module_lines_names in additional_modules_dict.items():
            module_line_dict[module_name] = module_lines_names
    if submodules_dict is not None:
        for module_name, module_submodules in submodules_dict.items():
            for submodule_name, lines_in_submodule in module_submodules.items():
                actual_lines = list(set(lines_in_submodule).intersection(set(line_num_dict.keys())))
                if not set(actual_lines).issubset(set(module_line_dict[module_name])):
                    raise ValueError('Submodule lines set is not a subset of module lines set')

                if len(actual_lines) > 0:
                    module_line_dict[submodule_name] = actual_lines
                    module_line_dict[module_name] = list(set(module_line_dict[module_name]) - set(actual_lines))
            if len(module_line_dict[module_name]) == 0:
                module_line_dict.pop(module_name)

    return module_line_dict


def read_all_input_data(path_to_data_file,
                        path_to_modules_definitions='',
                        modules_definitions_dict=None,
                        path_to_baseline_split='',
                        modules_constraints=False,
                        additional_modules_dict=None,
                        submodules_dict=None,
                        shrink_to_baseline=False):
    """
    Reads all required for optimization data. If no local files are present, generates two files: .pcl file containing
    event_line_matrix as "scipy.sparse.matrix" of type bool and .json file with "line_num_dict" as dictionary.
    Files are named according to used input data file using function _gen_names_input_file.
    Modules definitions are read from file or provided dict, if available.

    Parameters
    ----------
    path_to_data_file : string
        Path to data file of format ".json.gz" with HL2 decisions. Way to generate this file is described
        at YSDA/ turbo_stream_streaming repository at gitlab: https://gitlab.cern.ch/YSDA/turbo_stream_streaming
    path_to_modules_definitions : string
        Path to ".json" with modules definitions in format <module name> : <list of lines' names or regexp>
    modules_definitions_dict : dict {<module name> : <list of lines' names or regexp>
        Dictionary with modules definitions.
    path_to_baseline_split : string
        Path to ".json" file containing baseline streaming scheme in format
        {'stream_name': {'lines': {<lines names>}, 'prescale': <prescale value>}. If prescales are present,
        <prescale value> = {<line name>: <line prescale value>}, otherwise it's set to None
    modules_constraints : bool
        If True then lines are united into modules to run optimization with constraints
         (lines from one module must stay in one stream)
    additional_modules_dict : dict {<module_name>: <lines' names>}
        Additional modules for the existing module_line_dict.
    submodules_dict : dict {<module name> : dict {<submodule name>: <lines' names>}}
        Dictionary that shows into which parts should be divided specified modules. Every entry shows into which
        submodules current module's lines should be moved.
    shrink_to_baseline : bool
        If True only lines active in baseline streaming scheme are used and other are ignored

    Returns
    -------
    event_module_matrix : numpy.ndarray of type bool or None
        Matrix that shows event-module correspondence if modules definitions are present and "shrink_to_modules"
        is True. Otherwise set to None.
    event_line_matrix : numpy.ndarray of type bool
        Matrix that shows event-line correspondence.
    line_num_dict : dict {<line name> : <line number>}
        Line name to line number mapping (number is used e.g. in event_line_matrix or line_stream_matrix)
    module_line_name_dict : dict {<module name> : <lines' names>}
        Module name to list of line names corresponding to this module mapping.
    module_num_dict : dict {<module name> : <module number>}
        Module name to module number mapping (number is used e.g. in event_module_matrix or module_stream_matrix)
    baseline_scheme : numpy.ndarray of type bool
        Matrix that shows line-to-stream correspondence (True means line is included in stream) in baseline streams
        definitions.
    stream_num_dict : dict {<stream name> : <stream number>}
        Stream name to stream number mapping (number is used e.g. in line_stream_matrix)
    prescale_dict : dict {<line name> : <prescale value>}
        Dict with prescale values for lines from streams definitions
    """

    event_line_matrix_filename, line_num_dict_filename = _gen_names_from_input_file_name(path_to_data_file)
    if os.path.isfile(event_line_matrix_filename) and os.path.isfile(line_num_dict_filename):
        with open(event_line_matrix_filename) as fin:
            event_line_matrix = pickle.load(fin).toarray()
        with open(line_num_dict_filename) as lines_json:
            line_num_dict = json.load(lines_json)
    else:
        sparse_event_line_matrix, line_num_dict = \
            read_events_and_lines_from_raw(path_to_data_file, write_to_readable_format=True)
        event_line_matrix = sparse_event_line_matrix.toarray()

    line_num_dict = cast_unicode_to_str.convert(line_num_dict)
    print len(line_num_dict), 'Hlt2LowMultChiC2HH' in line_num_dict.keys()
    if not os.path.isfile(path_to_baseline_split):
        if path_to_baseline_split is not '':
            raise ValueError('File with baseline streams definitions is not found.')

        baseline_scheme = None
        stream_num_dict = None
        prescale_dict = None
    else:
        baseline_scheme, stream_num_dict, prescale_dict = read_scheme_from_defs(line_num_dict, path_to_baseline_split)
        if shrink_to_baseline:
            [event_line_matrix, line_num_dict, baseline_scheme, stream_num_dict]\
                = drop_unused_lines(event_line_matrix,
                                    line_num_dict,
                                    baseline_scheme,
                                    path_to_baseline_split)
    event_module_matrix = None
    module_line_dict = None
    module_num_dict = None
    print len(line_num_dict), 'Hlt2LowMultChiC2HH' in line_num_dict.keys()
    if modules_constraints:
        module_line_dict = read_modules_dict(line_num_dict,
                                             path_to_modules_definitions=path_to_modules_definitions,
                                             modules_definitions_dict=modules_definitions_dict)
        module_line_dict = add_submodules_and_extra_modules(line_num_dict,
                                                            module_line_dict,
                                                            additional_modules_dict,
                                                            submodules_dict)

        if module_line_dict is None:
            raise ValueError('Modules definitions are not found!')

        inactive_modules = np.array([len(x) == 0 for x in module_line_dict.values()]).nonzero()[0]
        for name in [module_line_dict.keys()[x] for x in inactive_modules]:
            module_line_dict.pop(name)

        n_modules = len(module_line_dict)
        event_module_matrix = np.zeros((event_line_matrix.shape[0], n_modules), dtype=np.bool)
        for i in range(n_modules):
            module_active_events = _get_lines_active_events(event_line_matrix,
                                                            [line_num_dict[line_name] for line_name in
                                                             module_line_dict[module_line_dict.keys()[i]]])
            for x in module_active_events:
                event_module_matrix[x, i] = True
        module_num_dict = dict(zip(module_line_dict.keys(), range(len(module_line_dict.keys()))))

    return [
            event_module_matrix,
            event_line_matrix,
            line_num_dict,
            module_line_dict,
            module_num_dict,
            baseline_scheme,
            stream_num_dict,
            prescale_dict
            ]
