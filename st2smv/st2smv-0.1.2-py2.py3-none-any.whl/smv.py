## Copyright (c) 2015-2017, Blake C. Rawlings.
##
## This file is part of `st2smv`.

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import copy
import json
import networkx
import os
import shutil

import pkg_resources

import pyparsing

from . import ast
from . import ir
from . import plugins
from . import st
from . import utils

logger = utils.logging.getLogger(__name__)

NUSMV_2_6_0_KEYWORDS = (
    'MODULE', 'DEFINE', 'MDEFINE', 'CONSTANTS', 'VAR',
    'IVAR', 'FROZENVAR', 'INIT', 'TRANS', 'INVAR', 'SPEC',
    'CTLSPEC', 'LTLSPEC', 'PSLSPEC', 'COMPUTE', 'NAME',
    'INVARSPEC', 'FAIRNESS', 'JUSTICE', 'COMPASSION', 'ISA',
    'ASSIGN', 'CONSTRAINT', 'SIMPWFF', 'CTLWFF', 'LTLWFF',
    'PSLWFF', 'COMPWFF', 'IN', 'MIN', 'MAX', 'MIRROR', 'PRED',
    'PREDICATES', 'process', 'array', 'of', 'boolean', 'integer',
    'real', 'word', 'word1', 'bool', 'signed', 'unsigned',
    'extend', 'resize', 'sizeof', 'uwconst', 'swconst', 'EX',
    'AX', 'EF', 'AF', 'EG', 'AG', 'E', 'F', 'O', 'G', 'H', 'X',
    'Y', 'Z', 'A', 'U', 'S', 'V', 'T', 'BU', 'EBF', 'ABF', 'EBG',
    'ABG', 'case', 'esac', 'mod', 'next', 'init', 'union', 'in',
    'xor', 'xnor', 'self', 'TRUE', 'FALSE', 'count'
)
SYNTHSMV_KEYWORDS = ('SYNTH', 'CTRBL')
KEYWORDS = NUSMV_2_6_0_KEYWORDS + SYNTHSMV_KEYWORDS

## `_COMPARISONS` tracks Boolean variables that are created to take
## the place of numeric comparisons when converting IR to an SMV
## model.
##
## TODO: get rid of this global variable (hack).
_COMPARISONS = set()


def convert_symbol(symbol):
    """Convert a symbol from AST/IR syntax to SMV syntax."""
    mapping = {
        ast.AND: '&',
        ast.OR: '|',
        ast.XOR: 'xor',
        ast.NOT: '!',
        ast.LT: 'lt',
        ast.LEQ: 'le',
        ast.GT: 'gt',
        ast.GEQ: 'ge',
        ast.MLT: 'mul',
        ast.SUB: 'min',
        ast.ADD: 'pls',
        ast.DIV: 'div',
        ast.NEG: 'neg',
        'ABS': 'ABS',
        'POS': 'pos',
        ir.EQ_BOOLEAN: '=',
        ir.NEQ_BOOLEAN: '!=',
        ir.EQ_NUMERIC: 'eq',
        ir.NEQ_NUMERIC: 'ne',
        ast.EQ: 'eq',
        ast.NEQ: 'ne',
        ast.BOOLEAN: 'boolean',
    }
    for key in mapping:
        if key == symbol:
            return mapping[key]
    raise ir.ConversionError('Unrecognized symbol: {0}'.format(symbol))


@utils.timing(log_fun=logger.info, log_text='Converted the ST file: {:.2f}s')
def st_to_smv(
        fname,
        metadata_paths=(),
        directory=None,
        loaded_plugins=None,
        plugin_options=None,
):
    """Convert the Structured Text file `fname` to an SMV model.

    This writes the model (and possibly other output) and returns the
    `Converter` object.

    """
    if loaded_plugins is None:
        loaded_plugins = []
    if plugin_options is None:
        plugin_options = {}

    ## Parse the input file.
    tree = st.get_ast(fname)

    ## Check for any plugins that do AST transformations, and apply
    ## them.
    for plugin in plugins.actions.get_active_plugins(
            loaded_plugins, plugins.actions.AST_TRANSORMATIONS
    ):
        transformer = plugin.Transformer()
        transformed = transformer.transform_ast(tree)
        tree = transformed
        logger.debug(
            'Applied AST transformations from the "{}" plugin.'
            .format(plugin.NAME)
        )

    ## Save the AST in `directory`.
    ast.write_ast(tree, directory=directory)

    ## Convert the AST to IR.
    conv = ir.Converter(loaded_plugins)
    conv.metadata_paths = metadata_paths
    conv.plugin_options = plugin_options
    conv.convert_ast(tree)
    conv.infer_types()
    conv.generate_model()

    ## Make the IR an SMV module.
    initializing = ir.Var('initializing', None)
    conv.intermediate_representation = [
        ['MODULE', 'main'],
        [ast.ASSIGN, [['init', initializing], ir.Var('TRUE', None)]],
        [ast.ASSIGN, [['next', initializing], ir.Var('FALSE', None)]],
    ] + conv.intermediate_representation

    ## Run some sanity checks on the IR.
    conv.check_smv_variables()

    ## Write some output now.
    if directory is not None:
        if not os.path.isdir(directory):
            os.mkdir(directory)
    write_tests(conv, directory)
    if len(conv.abstractions) > 0:
        write_abstractions(conv, directory)
    if len(conv.coi_info) > 0:
        write_coi_info(conv, directory)
    copy_auxiliary(conv, directory)

    ## Write the output.
    path = directory + os.sep + 'model.json'
    with open(path, 'w') as f:
        json.dump(
            conv.intermediate_representation, f,
            indent=2, separators=(',', ': '),
            sort_keys=True,
            cls=ir.JSONEncoder
        )
        f.write('\n')

    return conv


def write_tests(conv, directory):
    """Write process-independent tests (PITs) in `directory`/pits/."""

    ## Plugins.
    plugin_pits = []
    for plugin in plugins.actions.get_active_plugins(
            conv.loaded_plugins, plugins.actions.PROCESS_INDEPENDENT_TESTS
    ):
        new = plugin.generate_pits(conv)
        for old in plugin_pits:
            assert old['PIT_PREFIX'] != new['PIT_PREFIX']
        plugin_pits.append(new)

    ## Combine the tests.
    tests = {}
    pit_dicts = plugin_pits
    for pit_dict in pit_dicts:
        for key in pit_dict:
            if key == 'PIT_PREFIX':
                continue
            if key not in tests:
                tests[key] = []
            tests[key] += pit_dict[key]

    ## Write the PITs.
    pit_dir = directory + os.sep + 'pits'
    if not os.path.isdir(pit_dir):
        os.mkdir(pit_dir)
    for key in tests:
        path = pit_dir + os.sep + '{}.smv'.format(key)
        with open(path, 'w') as f:
            f.write('\n'.join(tests[key]))
            f.write('\n')

    return


def write_abstractions(conv, directory):
    """Write the abstractions in `directory`/abstractions."""
    abstractions_dir = directory + os.sep + 'abstractions'
    if not os.path.isdir(abstractions_dir):
        os.mkdir(abstractions_dir)
    for abstraction_type in conv.abstractions:
        for key in conv.abstractions[abstraction_type]:
            path = (
                abstractions_dir
                + os.sep
                + '{}-{}.json'.format(abstraction_type, key)
            )
            with open(path, 'w') as f:
                json.dump(
                    conv.abstractions[abstraction_type][key], f,
                    indent=2, separators=(',', ': '),
                    sort_keys=True,
                    cls=ir.JSONEncoder
                )
                f.write('\n')
    return


def write_coi_info(conv, directory):
    """Write the COI info in `directory`."""
    with open(directory + os.sep + 'coi_info.json', 'w') as f:
        json.dump(
            conv.coi_info, f,
            indent=2, separators=(',', ': '),
            sort_keys=True,
            cls=ir.JSONEncoder
        )
        f.write('\n')
    return


def copy_auxiliary(conv, directory):
    """Copy some auxiliary files (SMV modules, etc.) to `directory`."""
    aux_names = ['Makefile.run']
    if 'timers' in conv.special_variables:
        aux_names.append('delay_timer.smv')
    for aux_name in aux_names:
        aux_location = pkg_resources.resource_filename(__name__, aux_name)
        shutil.copyfile(
            aux_location,
            directory + os.sep + aux_name
        )


def combine(infiles, metadatas, variables, loaded_plugins, plugin_options):
    """Combine multiple SMV components to form a single model.

    The input files `infiles` can be a mix of either JSON files
    containing IR or raw SMV files, and the metadata files `metadata`
    should be JSON files with additional metadata, such as
    abstractions (which are applied when combining the files).

    """
    _COMPARISONS.clear()
    (cone_of_influence, deleted) = get_coi_and_deleted_variables(
        metadatas, variables, loaded_plugins, plugin_options
    )
    modules = []
    raw = []
    output = []
    for infile in infiles:
        with open(infile, 'r') as f:
            if infile.endswith('smv'):
                lines = f.readlines()
                if any(['MODULE' in l for l in lines]):
                    modules += lines
                else:
                    raw += lines
            else:
                ## Structured (JSON) input, easy to do the
                ## replacements.
                assert infile.endswith('json')
                statements = json.load(f, object_hook=ir.json_decode_hook)
                if variables is None or None in (cone_of_influence, deleted):
                    logger.warning(
                        'COI info is not available, '
                        'no abstractions will be applied.'
                    )
                    intermediate_representation = statements
                else:
                    intermediate_representation = []
                    for statement in statements:
                        ## Skip assignments to non-influencing variables.
                        if statement[0] in (ast.ASSIGN, ir.DEFINE):
                            ## Find out what the LHS variable is.
                            if isinstance(statement[1][0], ir.Var):
                                var = statement[1][0]
                            else:
                                assert statement[1][0][0] in ('init', 'next')
                                var = statement[1][0][1]
                            if not isinstance(var, ir.Var):
                                logger.error(
                                    'Could not determine LHS variable '
                                    'in assignment: {}'
                                    .format(statement)
                                )
                                assert False
                            ## Skip any variables that aren't in the cone
                            ## of influence.
                            if var not in cone_of_influence:
                                if var in deleted:
                                    logger.error(
                                        'Deleted variable not in COI: {}'
                                        .format(var)
                                    )
                                    assert False
                                if var.field is None:
                                    continue
                            ## Replace the `deleted` variables with dummy
                            ## inputs.
                            if var in deleted:
                                if var not in cone_of_influence:
                                    logger.error(
                                        'Deleted variable not in COI: {}'
                                        .format(var)
                                    )
                                    assert False
                                ivar = 'ivar_{}'.format(var)
                                intermediate_representation.append(
                                    ('IVAR', ivar, 'boolean')
                                )
                                intermediate_representation.append(
                                    ('VAR', var, 'boolean')
                                )
                                intermediate_representation.append(
                                    (ast.ASSIGN, (('next', var), ivar))
                                )
                                continue
                        ## Skip non-influencing statements.
                        elif not ir.is_in_coi(statement, cone_of_influence):
                            continue
                        ## At this point, we can't prove that the
                        ## statement doesn't influence the
                        ## specification, so include it in the model.
                        intermediate_representation.append(statement)
                output += ir_to_lines(intermediate_representation)

    if len(_COMPARISONS) > 0:
        output.append('-- Numeric comparisons, as Boolean variables:')
        for comparison in sorted(_COMPARISONS):
            output.extend(
                [
                    'IVAR ivar_{} : boolean;'.format(comparison),
                    'VAR {} : boolean;'.format(comparison),
                    'TRANS next({0}) = ivar_{0};'.format(comparison),
                ]
            )

    for line in modules + output + raw:
        print(line.strip())


def get_coi_and_deleted_variables(
        metadatas, variable_strings, loaded_plugins, plugin_options
):
    """Compute the cone of influence and deleted variables."""
    initializing = ir.Var('initializing', None)
    deleted_variables = set()
    cone_of_influence = {initializing}
    if variable_strings is None:
        ## Load the already-generated COI info.
        for metadata in metadatas:
            if os.path.exists(metadata):
                ## Check the metadata file for things like deleted nodes,
                ## etc.
                with open(metadata, 'r') as f:
                    s = f.read()
                    try:
                        j = json.loads(s, object_hook=ir.json_decode_hook)
                    except ValueError:
                        logger.warning(
                            'Could not read JSON metadata: {}'.format(metadata)
                        )
                        j = {}
                    deleted_variables |= set(j.get('deleted', []))
                    cone_of_influence |= set(j.get('coi', []))
            else:
                if len(metadata) > 0:
                    logger.warning('Missing metadata file: {}'.format(metadata))
    else:
        try:
            ## Compute the COI info on the fly.
            assert len(metadatas) == 1
            with open(metadatas[0], 'r') as f:
                s = f.read()
                j = json.loads(s, object_hook=ir.json_decode_hook)
            edges = j['edges']
            node2var = {int(key): value for (key, value) in j['node2var'].items()}
            untouchable = j['untouchable']
            digraph = networkx.DiGraph(edges)
            all_variables = {node2var[k] for k in node2var}
            variables = {ir.str2var(x, all_variables) for x in variable_strings}
            active_plugins = plugins.actions.get_active_plugins(
                loaded_plugins, plugins.actions.ABSTRACTION
            )
            assert len(active_plugins) == 1
            plugin = active_plugins[0]
            (
                deleted, size, size0, target, coi
            ) = plugin.get_variable_cuts(
                digraph, node2var,
                variables, plugin_options, untouchable,
            )
            cone_of_influence |= coi
            deleted_variables |= deleted
        except AssertionError:
            logger.warning('Could not compute the COI info.')
            return (None, None)
    ## Do some cleanup and reporting.
    structures = set()
    for coi_var in cone_of_influence:
        if coi_var.field is not None:
            structure = copy.deepcopy(coi_var)
            structure.field = None
            structures.add(structure)
    cone_of_influence |= structures
    for var in deleted_variables:
        logger.debug('Deleting variable logic: {}'.format(var))
        assert isinstance(var, ir.Var)
    ##
    return (cone_of_influence, deleted_variables)


def ir_to_lines(tree, insert_comments=False):
    """Convert the IR `tree` to lines of SMV code."""
    assert isinstance(tree, (tuple, list))
    VARs = set()
    IVARs = set()
    lines = []
    for chunk in tree:
        assert isinstance(chunk, (tuple, list))
        if chunk[0] == 'MODULE':
            assert len(chunk) == 2
            lines.append(
                '{} {}'.format(
                    chunk[0],
                    ir_to_expression(chunk[1])
                )
            )
        elif chunk[0] in ('VAR', 'IVAR'):
            assert len(chunk) == 3
            var = chunk[1]
            rhs = chunk[2]
            ## Track declarations.
            if chunk[0] == 'VAR':
                category = VARs
            elif chunk[0] == 'IVAR':
                category = IVARs
            else:
                assert False
            if var not in category:
                category.add(var)
                if rhs not in (ast.NUMERIC, ast.VALUE):
                    lines.append(
                        '{} {} : {};'.format(
                            chunk[0],
                            ir_to_expression(var),
                            ir_to_expression(rhs)
                        )
                    )
                else:
                    logger.debug(
                        'Skipping variable declaration: {}'.format(chunk)
                    )
        elif chunk[0] == ast.ASSIGN:
            assert len(chunk) == 2
            assert len(chunk[1]) == 2
            lhs = ir_to_expression(chunk[1][0])
            rhs = ir_to_expression(chunk[1][1])
            ## Track declarations.
            if isinstance(chunk[1][0], (tuple, list)):
                assert len(chunk[1][0]) == 2
                assert chunk[1][0][0] in ('next', 'init')
                lhs_var = chunk[1][0][1]
            else:
                lhs_var = chunk[1][0]
                assert isinstance(lhs_var, ir.Var)
            if not (isinstance(lhs_var, ir.Var) or lhs_var is None):
                print(lhs_var)
                print(type(lhs_var))
                assert False
            if isinstance(lhs_var, ir.Var):
                if lhs_var not in VARs:
                    VARs.add(lhs_var)
                    lines.append('VAR {} : {};'.format(lhs_var, 'boolean'))
            ##
            lines.append('ASSIGN {} := {};'.format(lhs, rhs))
        elif chunk[0] in (ir.CTRBL, ir.INVAR):
            assert len(chunk) == 2
            lines.append(
                '{} {};'.format(
                    chunk[0],
                    ir_to_expression(chunk[1])
                )
            )
        elif chunk[0] == ir.TRANS:
            assert len(chunk) == 2
            lines.append(
                '{} {};'.format(
                    'TRANS',
                    ir_to_expression(chunk[1])
                )
            )
        elif chunk[0] == ir.DEFINE:
            assert len(chunk) == 2
            assert len(chunk[1]) == 2
            lines.append(
                '{} {} := {};'.format(
                    chunk[0],
                    ir_to_expression(chunk[1][0]),
                    ir_to_expression(chunk[1][1])
                )
            )
        elif chunk[0] == 'PIT':
            assert len(chunk) == 2
            lines.append('\n'.join(chunk[1]))
        elif chunk[0] == 'ASSIGN_NUMERIC':
            if insert_comments is False:
                pass
            else:
                lines.append(
                    '-- numeric assignment to {}'
                    .format(ir_to_expression(chunk[1][0]))
                )
        elif chunk[0] == 'ASSIGN_VALUE':
            if insert_comments is False:
                pass
            else:
                lines.append(
                    '-- untyped assignment to {}'
                    .format(ir_to_expression(chunk[1][0]))
                )
        else:
            logger.error(
                'Unrecognized statement in intermediate representation: {}'
                .format(repr(chunk))
            )
    assert len(set.intersection(VARs, IVARs)) == 0
    return lines


def ir_to_expression(tree, no_grouping=False):
    """Convert the IR expression `tree` to an SMV expression."""
    ## Base cases.
    if isinstance(tree, (ir.Var, utils.six.string_types)):
        try:
            return convert_symbol(tree)
        except ir.ConversionError:
            return str(tree)
    else:
        assert isinstance(tree, (tuple, list))
        assert len(tree) > 0

    ## Recursive cases.
    if len(tree) == 1:
        if no_grouping:
            format_string = '{}'
        else:
            format_string = '({})'
        return format_string.format(
            ir_to_expression(tree[0], no_grouping=no_grouping)
        )
    elif tree[0] in ('next', 'init'):
        assert len(tree) == 2
        return '{}({})'.format(tree[0], ir_to_expression(tree[1]))
    elif tree[0] in ast.unary_boolean_operators:
        assert len(tree) == 2
        return '({} {})'.format(
            convert_symbol(tree[0]), ir_to_expression(tree[1])
        )
    elif tree[0] in ir.binary_boolean_operators:
        assert len(tree) == 2
        return '({} {} {})'.format(
            ir_to_expression(tree[1][0]),
            convert_symbol(tree[0]),
            ir_to_expression(tree[1][1]),
        )
    elif tree[0] in ast.unary_arithmetic_operators + ('ABS', 'POS'):
        assert len(tree) == 2
        rhs = ir_to_expression(tree[1], no_grouping=True)
        return ir.Var(
            '{0}__{1}'.format(convert_symbol(tree[0]), rhs),
            None
        )
    elif tree[0] in ir.binary_numeric_operators + ast.comparators:
        assert len(tree) == 2
        retval = ir.Var(
            '{0}__{1}__{2}'.format(
                ir_to_expression(tree[1][0], no_grouping=True),
                convert_symbol(tree[0]),
                ir_to_expression(tree[1][1], no_grouping=True),
            ), None
        )
        if tree[0] not in ast.binary_arithmetic_operators:
            _COMPARISONS.add(retval)
        return retval
    elif tree[0] == 'case':
        assert len(tree) == 2
        cases = [
            '{} : {};'.format(
                ir_to_expression(pair[0]),
                ir_to_expression(pair[1]),
            )
            for pair in tree[1]
        ]
        return 'case {} esac'.format(
            ' '.join(cases)
        )
    elif tree[0] == ir.ONE_OR_MORE:
        assert len(tree[1]) > 0
        return '(count({}) > {})'.format(
            ', '.join([str(ir_to_expression(x)) for x in tree[1]]),
            ir.Var('0', None)
        )
    elif tree[0] == ir.ONE_AT_MOST:
        assert len(tree[1]) > 0
        return '(count({}) <= {})'.format(
            ', '.join([str(ir_to_expression(x)) for x in tree[1]]),
            ir.Var('1', None)
        )
    elif tree[0] == ir.ONE_AND_ONLY_ONE:
        assert len(tree[1]) > 0
        return '(count({}) = {})'.format(
            ', '.join([str(ir_to_expression(x)) for x in tree[1]]),
            ir.Var('1', None)
        )
    elif len(tree) > 1:
        logger.debug(
            'Treating the TREE as a function call: {}'.format(repr(tree))
        )
        return '{}({})'.format(
            ir_to_expression(tree[0]),
            ', '.join(
                [str(ir_to_expression(x)) for x in tree[1:]]
            )
        )
    else:
        logger.error(
            'Unrecognized expression in intermediate representation: {}'
            .format(repr(tree))
        )


def postprocess(loaded_plugins):
    """Post-process the test results in the current directory."""
    results = {}
    times = {}

    ## Find the output files.
    files = os.listdir('.')
    cex_suffix = '.cex'
    prop_suffix = '.prop'
    cex_paths = []
    prop_paths = []
    for fname in files:
        if fname.endswith(cex_suffix):
            cex_paths.append(fname)
        elif fname.endswith(prop_suffix):
            prop_paths.append(fname)
    ## TODO: make sure that `cex` and `prop` match up
    cex_paths = sorted(cex_paths)
    prop_paths = sorted(prop_paths)

    ## Read the output.
    cexs = [_parse_counterexamples(x) for x in cex_paths]
    props = [_parse_properties(x) for x in prop_paths]
    timing_infos = [_parse_timing_info(x) for x in cex_paths]

    ## Apply any plugins that handle specific result types.
    active_plugins = plugins.actions.get_active_plugins(
        loaded_plugins, plugins.actions.POSTPROCESS
    )
    for idx, cex in enumerate(cexs):
        prop = props[idx]
        for plugin in active_plugins:
            categories = plugin.get_postprocessing_categories()
            plugin_results = _postprocess_worker(cex, prop, categories)
            _merge_dicts_of_sets(results, plugin_results)

    ## Get the timing information.
    for idx, cex_path in enumerate(cex_paths):
        timing_info = timing_infos[idx]
        name = cex_path[:-len(cex_suffix)]
        times[name] = timing_info
    with open('timing.json', 'w') as f:
        json.dump(
            times, f,
            indent=2, separators=(',', ': '), sort_keys=True
        )
        f.write('\n')

    ## Print the results.
    if False:
        for key in sorted(results):
            value = results[key]
            print('## {} ({})'.format(key, len(value)))
            for label in sorted(value):
                print(label)
    with open('summary.json', 'w') as f:
        results_serializable = {
            key: sorted(results[key])
            for key in sorted(results)
        }
        json.dump(
            results_serializable, f,
            indent=2, separators=(',', ': '), sort_keys=True
        )
        f.write('\n')


def _postprocess_worker(cex, prop, categories):
    results = {}
    for p in prop:
        property_specification = p[0][2].strip()
        property_logic = p[1][0]
        name = p[1][3]
        ## Find the matching result.
        for c in cex:
            counterexample_specification = c[1].strip()
            counterexample_logic = c[0]
            if counterexample_specification == property_specification:
                if property_logic == 'CTL':
                    if counterexample_logic[0] == 'specification':
                        break
                if property_logic == 'SYNTH':
                    if counterexample_logic[0] == '(SYNTH)':
                        break
        else:
            assert False
        outcome = c[-1]

        for category in categories:
            result_type = category[0]
            property_type = category[1]
            outcome_test = category[2]
            if result_type not in results:
                results[result_type] = set()
            if name.startswith(property_type):
                if outcome == outcome_test:
                    label = name[len(property_type)+1:]
                    results[result_type].add(label)

    return results


def _merge_dicts_of_sets(current, new):
    """Merge the elements of `new` into `current` (via set union).

    Both `new` and `current` must be `dict`s whose values are `set`s.
    This modifies `current`.

    """
    for key in new:
        if key in current:
            current[key] |= new[key]
        else:
            current[key] = new[key]


def _parse_counterexamples(path):
    """Parse the counterexample file `path`."""
    BEGIN = pyparsing.Literal('--')
    LPAR = pyparsing.Literal('(')
    RPAR = pyparsing.Literal(')')
    TYPE = pyparsing.Combine(LPAR + pyparsing.Word(pyparsing.alphas) + RPAR)
    SPECIFICATION = pyparsing.Literal('specification')
    IS = pyparsing.Literal('is')
    OUTCOME = (pyparsing.Literal('true') | pyparsing.Literal('false'))

    result = pyparsing.Group(
        BEGIN.suppress()
        + pyparsing.Group(pyparsing.Optional(TYPE) + SPECIFICATION)
        + pyparsing.SkipTo(IS + OUTCOME, include=True)
    )

    with open(path) as f:
        lines = f.readlines()
    matches = []
    for line in lines:
        if not line.startswith('--'):
            continue
        else:
            try:
                match = result.parseString(line)[0].asList()
            except pyparsing.ParseException:
                continue
            matches.append(match)
    return matches


def _parse_properties(path):
    """Parse the properties file `path`."""
    ## First line.
    NUMBER = pyparsing.Word(pyparsing.nums)
    COLON = pyparsing.Literal(':')
    line_1 = pyparsing.Group(NUMBER + COLON + pyparsing.restOfLine)
    ## Second line.
    LSQ = pyparsing.Literal('[')
    RSQ = pyparsing.Literal(']')
    STUFF = pyparsing.Regex(r'[\w/]+')
    line_2 = pyparsing.Group(
        LSQ.suppress() + STUFF + STUFF + STUFF + STUFF + RSQ.suppress()
    )
    ## Parse line-by-line.
    first_lines = []
    second_lines = []
    with open(path, 'r') as f:
        lines = f.readlines()
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(('***', '---')) or len(stripped) == 0:
            continue
        try:
            parsed = line_1.parseString(line)
            first_lines.append(parsed.asList()[0])
            continue
        except pyparsing.ParseException:
            pass
        try:
            parsed = line_2.parseString(line)
            second_lines.append(parsed.asList()[0])
            continue
        except pyparsing.ParseException:
            pass
    assert len(first_lines) == len(second_lines)
    ##
    return list(zip(first_lines, second_lines))


def _parse_timing_info(path):
    """Read the timing information form the SMV output at `path`."""
    ## Define a parser for the timing info line.
    DIGITS = pyparsing.Word(pyparsing.nums)
    NUMBER = pyparsing.Combine(DIGITS + '.' + DIGITS)
    BEGINNING = 'User time'
    parser = BEGINNING + NUMBER + pyparsing.Word(pyparsing.alphas)
    ## Find the lines in the file with timing info.
    with open(path) as f:
        lines = f.readlines()
    relevant_lines = [line for line in lines if line.startswith(BEGINNING)]
    if not len(relevant_lines) == 1:
        logger.warning(path)
        assert False
    relevant_line = relevant_lines[0]
    ## Parse the timing info line.
    parsed = parser.parseString(relevant_line).asList()
    user_time = float(parsed[1])
    units = parsed[2]
    return (user_time, units)
