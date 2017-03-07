def bind_action_creator(action_creator, dispatch):
    return lambda *args: dispatch(action_creator(*args))


def bind_action_creators(action_creators, dispatch):
    if callable(action_creators):
        return bind_action_creator(action_creators, dispatch)
    if type(action_creators) is not dict or not action_creators:
        raise Exception(
            'bind_action_creators expected a dict or a callable, instead '
            'received {}.'.format(type(action_creators))
        )

    bound_action_creators = {}
    for key, action_creator in action_creators.iteritems():
        if callable(action_creator):
            bound_action_creators[key] = bind_action_creator(
                action_creator, dispatch)
    return bound_action_creators
