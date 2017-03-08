## Copyright (c) 2016, Blake C. Rawlings.
##
## This file is part of `st2smv`.

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import json

from ... import ast
from ... import plugins
from ... import utils

logger = utils.logging.getLogger(__name__)

## Plugin information.
NAME = 'varlock'
ACTIONS = (
    plugins.actions.PROCESS_INDEPENDENT_TESTS,
    plugins.actions.POSTPROCESS,
)
OPTIONS = {
    'varlock_coi': (
        bool,
        (
            'when creating variable lock tests, '
            'include all the influencing variables'
        )
    )
}


def generate_pits(converter):
    pit_tmp = converter.assigned | converter.defined
    pit_tmp -= converter.aliases
    pit_tmp -= converter.ivars
    pit_tmp &= converter.unconditional_assignments
    pit_vars = sorted(
        {x for x in pit_tmp if (converter.get_type(x) == ast.BOOLEAN)}
    )

    pits = {'PIT_PREFIX': NAME}
    spec_types = (
        ('SPEC', 'varlock_potential'),
        ('SYNTH', 'varlock_guaranteed'),
    )
    include_coi = converter.plugin_options.get('varlock_coi')
    for var in pit_vars:
        ## Get the other variables that should factor in.
        coi = set()
        if not include_coi:
            others = set()
        else:
            coi_plugins = plugins.actions.get_active_plugins(
                converter.loaded_plugins, plugins.actions.INFLUENCE
            )
            for plugin in coi_plugins:
                coi |= plugin.get_cone_of_influence(converter, var)
            coi &= set(pit_vars)
            ## Ignore "known variable locks".
            known_varlocks_smv = _get_known_varlocks(converter)
            known_varlocks = {x for x in coi if str(x) in known_varlocks_smv}
            if var in known_varlocks:
                others = set()
            else:
                if len(known_varlocks) > 0:
                    logger.debug(
                        'Leaving known variable locks out of varlock test '
                        'for variable {}: {}'
                        .format(var, (known_varlocks & coi))
                    )
                others = (coi - known_varlocks) - {var}
        ## Build the specifications.
        inner = ' & '.join(
            [
                '(EF({0}) & EF(!{0}))'.format(x)
                for x
                in [var] + sorted(others)
            ]
        )
        pits[var] = []
        for spec_type in spec_types:
            pits[var].append(
                '{} NAME {}_{} := AG({});'
                .format(spec_type[0], spec_type[1], str(var), inner)
            )

    return pits


def _get_known_varlocks(converter):
    varlocks = set()
    for mp in converter.metadata_paths:
        with open(mp) as f:
            data = json.load(f)
        new_varlocks = set(data.get('varlocks', []))
        varlocks |= new_varlocks
    return varlocks


def get_postprocessing_categories():
    return (
        ('Potential Variable Locks', 'varlock_potential', 'false'),
        ('Guaranteed Variable Locks', 'varlock_guaranteed', 'false'),
    )
