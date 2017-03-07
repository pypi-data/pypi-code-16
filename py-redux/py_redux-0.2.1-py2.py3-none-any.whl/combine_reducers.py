import logging

from .create_store import action_types, frozenbunch

_logger = logging.getLogger(__name__)


def get_none_state_error_message(key, action):
    action_type = action and action.type
    action_name = (action_type and str(action_type)) or 'an action'
    return (
        'Given action {}, reducer "{}" returned None. To ignore an action, '
        'you must explicitly return the previous state. If you want this '
        'reducer to hold no value, you can return null instead of undefined.'
    ).format(action_name, key)


def get_unexpected_state_shape_warning_message(input_state,
                                               reducers,
                                               action,
                                               unexpected_key_cache):
    argument_name = (
        'preloaded_state argument passed to create_store' if
        action and action.type is action_types.INIT else
        'previous state received by the reducer')
    if not reducers:
        return (
            'Store does not have a valid reducer. Make sure the argument '
            'passed to combine_reducers is a dict whose values are reducers.'
        )
    if type(input_state) is not dict:
        return (
            'The {} has unexpected type of "{}". Expected argument to be a '
            'dict with the following keys: "{}"'
        ).format(
            argument_name,
            type(input_state),
            '", "'.join([str(k) for k in reducers.keys()])
        )
    unexpected_keys = [
        k
        for k in input_state
        if (k not in reducers and k not in unexpected_key_cache)]
    for k in unexpected_keys:
        unexpected_key_cache.add(k)
    if unexpected_keys:
        return (
            'Unexpected key{} "{}" found in {}. Expected to find one of the kn'
            'own reducer keys instead: "{}". Unexpected keys will be ignored.'
        ).format(
            's' if len(unexpected_keys) > 1 else '',
            '", "'.join([str(k) for k in unexpected_keys]),
            argument_name,
            '", "'.join([str(k) for k in reducers])
        )


def assert_reducer_sanity(reducers):
    for key, reducer in reducers.iteritems():
        initial_state = reducer(None, frozenbunch(type=action_types.INIT))
        if initial_state is None:
            raise Exception(
                'Reducer "{}" returned None during initialization. If the state '  # NOQA
                'passed to the reducer is None, you must explicitly return the'
                ' initial state. The initial state may not be None. If you don'
                '\'t want to set a value, use a falsy value or the False '
                'constant.'.format(key)
            )
        dummy_type = object()
        if reducer(None, frozenbunch(type=dummy_type)) is None:
            raise Exception(
                'Reducer "{}" returned None when probed with a random type. '
                'Don\'t try to handle {} or other actions in redux namespace. '
                'They are considered private. Instead, you must return the '
                'current state for any unknown actions, unless it is None, '
                'in which case you must return the initial state, regardless '
                'of the action type. The initial state may not be None.'
            )


def combine_reducers(reducers):
    final_reducers = {}
    for key, reducer in reducers.iteritems():
        if reducer is None:
            _logger.warn("No reducer provided for key {}".format(key))
        if callable(reducer):
            final_reducers[key] = reducer

    unexpected_key_cache = set()
    try:
        assert_reducer_sanity(final_reducers)
    except Exception as e:
        sanity_error = e

    # NOTE[ek] not defaulting state, bad?
    def combination(state, action):
        if sanity_error:
            raise sanity_error

        warning_message = get_unexpected_state_shape_warning_message(
            state, final_reducers, action, unexpected_key_cache)
        if warning_message:
            _logger.warn(warning_message)

        has_changed = False
        next_state = {}
        for key, reducer in final_reducers.iteritems():
            previous_state_for_key = state[key]
            next_state_for_key = reducer(previous_state_for_key, action)
            if next_state_for_key is None:
                error_message = get_none_state_error_message(key, action)
                raise Exception(error_message)
            next_state[key] = next_state_for_key
            has_changed = (
                has_changed or
                next_state_for_key is not previous_state_for_key)
        return next_state if has_changed else state
