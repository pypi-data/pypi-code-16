from .create_store import actiontypes, frozenbunch
from .apply_middleware import middleware


@middleware
def noop(store, get_next, action):
    return get_next(action)


@middleware
def doubler(store, get_next, action):
    get_next(action)
    return get_next(action)


@middleware
def logger(store, get_next, action):
    print("Dispatching: {}".format(action))
    result = get_next(action)
    print("Next state: {}".format(store.get_state()))
    return result


journaler_action_types = actiontypes('journaler_middleware', 'log shelve')


def journaler_print(): return frozenbunch(type=journaler_action_types.log)


def make_journaler_middleware():
    actions = []

    @middleware
    def middleware_fn(store, get_next, action):
        if action.type == journaler_action_types.log:
            print("Journaled history: {}".format(actions))
        actions.append(action)
        return get_next(action)
    return middleware_fn
