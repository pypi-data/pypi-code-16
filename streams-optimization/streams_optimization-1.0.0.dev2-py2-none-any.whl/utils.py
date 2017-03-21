import numpy as np


def modules_accordance_check(line_stream_matrix, module_line_dict):
    """
    Checks if streaming scheme satisfies modules constraints: every module should be a subset of only
    one stream. If some module lines are present in several streams or
    Parameters
    ----------
    line_stream_matrix : numpy.ndarray of type bool
        Matrix that shows line-to-stream correspondence (True means line is included in stream).
    module_line_dict : dict {<module name> : <lines' numbers>}
        Module name to list of line numbers corresponding to this module mapping.

    Returns
    -------
    bool
        True if scheme satisfies modules constraints. False otherwise.
    list of ints
        List of number of streams every module corresponds to. If constraints are satisfied, it contains only 1.
    """
    lines_in_stream = [set(list(np.where(line_stream_matrix[:, stream_index])[0]))
                       for stream_index in range(line_stream_matrix.shape[1])]
    module_flags = {}
    for module_name, module_lines in module_line_dict.items():
        flag = 0
        for lines_set in lines_in_stream:
            if set(module_lines).issubset(lines_set):
                flag += 1
        module_flags[module_name] = flag

    if all([flag == 1 for flag in module_flags.values()]):
        return True, module_flags
    else:
        return False, module_flags


def shrink_line_stream_matrix_to_modules(line_stream_matrix, module_line_dict, module_num_dict):
    """
    Shrinks line_stream_matrix to module case if it satisfies modules constraints.

    Parameters
    ----------
    line_stream_matrix : numpy.ndarray of type bool
        Matrix that shows line-to-stream correspondence (True means line is included in stream).
    module_line_dict : dict {<module name> : <lines' numbers>}
        Module name to list of line numbers corresponding to this module mapping.
    module_num_dict : dict {<module name> : <module number>}
        Module name to module number mapping (number is used e.g. in event_module_matrix or module_stream_matrix)

    Returns
    -------
    module_stream_matrix : numpy.ndarray of type bool
        Matrix that shows module-to-stream correspondence (True means module is included in stream).
    """

    if not modules_accordance_check(line_stream_matrix, module_line_dict)[0]:
        raise ValueError("line_stream_matrix doesn't meet modules constraints!")
    n_lines_ = line_stream_matrix.shape[0]
    module_stream_matrix = np.zeros((n_lines_, line_stream_matrix.shape[1]), dtype='bool')

    for module_name, lines_in_module in module_line_dict.items():
        stream_index = np.where(line_stream_matrix[lines_in_module[0], :])[0]
        module_stream_matrix[module_num_dict[module_name], stream_index] = True
    return module_stream_matrix


def restore_module_stream_matrix(module_stream_matrix, module_line_dict, module_num_dict, shape):
    """
    Unwraps module_stream_matrix to line_stream_matrix according to module_line_dict mapping.

    Parameters
    ----------
    module_stream_matrix : numpy.ndarray of type bool
        Matrix that shows module-to-stream correspondence (True means module is included in stream).
    module_line_dict : dict {<module name> : <lines' numbers>}
        Module name to list of line numbers corresponding to this module mapping.
    module_num_dict : dict {<module name> : <module number>}
        Module name to module number mapping (number is used e.g. in event_module_matrix or module_stream_matrix)
    shape : tuple (int, int)
        Shape of line_stream_matrix to be returned.

    Returns
    -------
    line_stream_matrix : numpy.ndarray of type bool
        Matrix that shows line-to-stream correspondence (True means line is included in stream).
    """

    line_stream_matrix = np.zeros(shape, dtype='bool')
    for module_name, lines_in_module in module_line_dict.items():
        if len(lines_in_module) == 0:
            continue
        stream_idx = np.where(module_stream_matrix[module_num_dict[module_name], :])[0][0]
        for line_idx in lines_in_module:
            line_stream_matrix[line_idx, stream_idx] = True
    return line_stream_matrix


def measure_weighted_storage(event_line_matrix, line_stream_matrix, line_num_dict, dict_of_params, prescale=None):
    """
    Computes used disk space approximation (S score) if line_stream_matrix is used to stream the data.
    S score is computed according to dict_of_params: every entry contains field 'mode' that shows, how
    the corresponding group of lines should be considered.
    For example, if
        dict_of_params = {'full': {'lines': <lines>, 'mode': 'indicator'},
                          'persist_reco': {'lines': <lines>, 'mode': 'indicator'},
                          'turbo': {'lines': <lines>, 'mode': 'sum'}},
    the S score is computed by the following formula:
        Stream weight = \sum_{events in stream} (event weight),
        where
        event weight = 60 * Indicator(event belongs to "full" line) +
                       50 * Indicator(event belongs to "persist_reco" line) + 10 * #("turbo" lines that contain event).
    Parameters
    ----------
    event_line_matrix : numpy.ndarray of type bool
        Matrix that shows event-line correspondence.
    line_stream_matrix : numpy.ndarray of type bool
        Matrix that shows line-to-stream correspondence (True means line is included in stream).
    line_num_dict : dict {<line name> : <line number>}
        Line name to line number mapping (number is used e.g. in event_line_matrix or line_stream_matrix)
    dict_of_params : dict {<group name>: {'lines': [<lines in group>], 'mode': <mode value, can be 'sum' or 'indicator>,
                                          'weight_value': int}}
    prescale : numpy.array of type float
        Array that contains prescale value for each line.
    Returns
    -------
    list of int values
        List of S scores for each stream accordingly.
    """
    n_lines = line_stream_matrix.shape[0]
    n_streams = line_stream_matrix.shape[1]
    stream_weights_list = []
    if prescale is None:
        prescale = np.ones(event_line_matrix.shape[1])

    def get_mask(lines_group):
        mask_for_lines_from_current_group = np.zeros(n_lines, dtype=np.bool)
        mask_for_lines_from_current_group[[line_num_dict[x] for x in lines_group['lines']
                                           if x in line_num_dict.keys()]] = True
        return mask_for_lines_from_current_group

    def get_lines_group_weigh_calculator(lines_group):
        if lines_group['mode'] == 'sum':
            def calculate_weights(event_group_correspondence):
                return lines_group['weight_value'] * event_group_correspondence.sum(axis=1).sum()
        elif lines_group['mode'] == 'indicator':
            def calculate_weights(event_group_correspondence):
                return lines_group['weight_value'] * (
                    1 - (1 - event_group_correspondence).prod(axis=1)).sum()
        else:
            raise ValueError("Unknown lines group mode: %s" % lines_group['mode'])
        return calculate_weights

    masks_and_calculators = list(map(lambda lines_group: (
        get_mask(lines_group), get_lines_group_weigh_calculator(lines_group)),
                                     dict_of_params.values()))

    prescaled_event_line_matrix = event_line_matrix * prescale
    for stream_idx in range(n_streams):
        stream_weight = 0
        for mask_for_lines_from_current_group, calculator_for_lines_from_current_group in \
                masks_and_calculators:
            group_in_stream = mask_for_lines_from_current_group * line_stream_matrix[:, stream_idx]
            event_group_correspondence = prescaled_event_line_matrix[:, group_in_stream]
            stream_weight += calculator_for_lines_from_current_group(event_group_correspondence)
        stream_weights_list.append(stream_weight)
    return stream_weights_list