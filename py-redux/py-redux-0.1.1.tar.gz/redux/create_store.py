from frozendict import frozendict


class frozenbunch(frozendict):
    def __init__(self, *args, **kwargs):
        super(frozenbunch, self).__init__(*args, **kwargs)
        self.__initialized = True

    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError as e:
            raise AttributeError(e)

    def __setattr__(self, attr, val):
        if '_frozenbunch__initialized' not in self.__dict__:
            return frozendict.__setattr__(self, attr, val)
        raise TypeError("asdf")

    def copy(self, **kwargs):
        for key in kwargs:
            if key not in self:
                raise TypeError("Cannot add new fields to a frozenbunch")
        return super(frozenbunch, self).copy(**kwargs)


def actiontypes(namespace, types):
    if type(types) is str:
        types = types.split(' ')
    return frozenbunch({
        t: "@@{}/{}".format(namespace, t) for t in types
    })


action_types = actiontypes('redux', 'INIT')
init_action = frozenbunch(type=action_types.INIT)


def create_store(reducer, preloaded_state=None, enhancer=None):
    if callable(preloaded_state) and enhancer is None:
        enhancer = preloaded_state
        preloaded_state = None

    if enhancer is not None:
        if not callable(enhancer):
            raise Exception("Expected the enhancer to be callable")
        return enhancer(create_store)(reducer, preloaded_state)

    if not callable(reducer):
        raise Exception("Expected the reducer to be callable")

    # Use function object because of python closure semantics
    # Assigning the variables in nested functions creates a local name
    state = lambda: None  # noqa
    state.current_reducer = reducer
    state.current_state = preloaded_state
    state.current_listeners = []
    state.next_listeners = []
    state.is_dispatching = False

    def ensure_can_mutate_next_listeners():
        if state.next_listeners is state.current_listeners:
            state.next_listeners = state.current_listeners[:]

    def get_state():
        return state.current_state

    def subscribe(listener):
        if not callable(listener):
            raise Exception("Expected listener to be callable")
        is_subscribed = True
        ensure_can_mutate_next_listeners()
        state.next_listeners.append(listener)

        def unsubscribe():
            if not is_subscribed:
                return
            ensure_can_mutate_next_listeners()
            state.next_listeners.remove(listener)

    def dispatch(action):
        try:
            action.type
        except AttributeError:
            raise Exception("Actions must have attribute 'type'")
        if state.is_dispatching:
            raise Exception("Reducers may not dispatch actions")

        try:
            state.is_dispatching = True
            state.current_state = state.current_reducer(
                state.current_state, action)
        finally:
            state.is_dispatching = False

        listeners = state.current_listeners = state.next_listeners
        for listener in listeners:
            listener()

        return action

    def replace_reducer(next_reducer):
        if not callable(next_reducer):
            raise Exception("Expected the next_reducer to be callable")
        state.current_reducer = next_reducer
        dispatch(init_action)

    # NOTE[ek] did not implement observable

    dispatch(init_action)

    return frozenbunch(dispatch=dispatch,
                       subscribe=subscribe,
                       get_state=get_state,
                       replace_reducer=replace_reducer)
