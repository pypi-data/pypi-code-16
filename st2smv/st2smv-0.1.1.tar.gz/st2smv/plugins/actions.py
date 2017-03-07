## Copyright (c) 2016, Blake C. Rawlings.
##
## This file is part of `st2smv`.

SPECIAL_EXPRESSIONS = object()
TRANSITION_LOGIC = object()
UNTOUCHABLE = object()
METADATA_CONSTRAINTS = object()
AST_TRANSORMATIONS = object()
ABSTRACTION = object()
REFINEMENT = object()
PROCESS_INDEPENDENT_TESTS = object()
INFLUENCE = object()
POSTPROCESS = object()

def get_active_plugins(loaded_plugins, action):
    """Return the list of loaded plugins that perform `action`."""
    return [
        plugin
        for plugin in loaded_plugins
        if action in plugin.ACTIONS
    ]
