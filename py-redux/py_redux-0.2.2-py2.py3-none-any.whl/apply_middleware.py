from .compose import compose
from .create_store import frozenbunch


def apply_middleware(*middlewares):
    def bind_create_store(create_store):
        def enhanced_create_store(reducer, preloaded_state, enhancer=None):
            store = create_store(reducer, preloaded_state, enhancer)
            dispatch = store.dispatch
            chain = []
            partial_store = frozenbunch(
                get_state=store.get_state,
                dispatch=lambda action: dispatch(action))
            chain = [m(partial_store) for m in middlewares]
            dispatch = compose(*chain)(store.dispatch)
            return store.copy(dispatch=dispatch)
        return enhanced_create_store
    return bind_create_store


def middleware(func):
    ''' Decorator for func(store, get_next, action)
    to more tersely make a middleware function '''
    return lambda store: lambda get_next: lambda action: func(
        store, get_next, action)
