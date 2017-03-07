from .create_store import actiontypes, frozenbunch


def noop(store):
    def bind_reducer(reducer):
        def apply_reducer(action):
            return reducer(action)
        return apply_reducer
    return bind_reducer


def doubler(store):
    def bind_reducer(reducer):
        def apply_reducer(action):
            reducer(action)
            return reducer(action)
        return apply_reducer
    return bind_reducer


def logger(store):
    def bind_reducer(reducer):
        def apply_reducer(action):
            print("Dispatching: {}".format(action))
            result = reducer(action)
            print("Next state: {}".format(store.get_state()))
            return result
        return apply_reducer
    return bind_reducer


journaler_action_types = actiontypes('journaler_middleware', 'log shelve')


def journaler_print(): return frozenbunch(type=journaler_action_types.log)


def journaler(store):
    def bind_reducer(reducer):
        actions = []

        def apply_reducer(action):
            if action.type == journaler_action_types.log:
                print("Journaled history: {}".format(actions))
            actions.append(action)
            return reducer(action)
        return apply_reducer
    return bind_reducer
