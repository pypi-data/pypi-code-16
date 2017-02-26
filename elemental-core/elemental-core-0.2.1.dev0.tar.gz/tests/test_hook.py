import elemental_core


_simple_handler_results = []
_defaulted_handler_results = []


def _simple_handler(sender, data):
    _simple_handler_results.append((sender, data))


def _defaulted_handler(sender, data):
    _defaulted_handler_results.append((sender, data))


class HasHooks(object):
    simple_hook = elemental_core.Hook()
    defaulted_hook = elemental_core.Hook(default_data_value='Test')

    def activate_simple_hook(self):
        self.simple_hook(self)
        self.simple_hook(self, 'SimpleValue')

    def activate_defaulted_hook(self):
        self.defaulted_hook(self)
        self.defaulted_hook(self, 'NonDefaultValue')


def test_hook_add_remove():
    has_hooks = HasHooks()

    has_hooks.simple_hook.add_handler(_simple_handler)

    assert len(has_hooks.simple_hook._handler_refs) == 1

    has_hooks.simple_hook.remove_handler(_simple_handler)

    assert len(has_hooks.simple_hook._handler_refs) == 0


def test_hook_iadd_isub():
    has_hooks = HasHooks()

    has_hooks.simple_hook += _simple_handler

    assert len(has_hooks.simple_hook._handler_refs) == 1

    has_hooks.simple_hook -= _simple_handler

    assert len(has_hooks.simple_hook._handler_refs) == 0


def test_simple_hook():
    has_hooks = HasHooks()

    has_hooks.simple_hook += _simple_handler
    has_hooks.activate_simple_hook()

    assert len(_simple_handler_results) == 2
    assert _simple_handler_results[0][0] is has_hooks
    assert _simple_handler_results[0][1] is None
    assert _simple_handler_results[1][0] is has_hooks
    assert _simple_handler_results[1][1] == 'SimpleValue'

    while _simple_handler_results:
        _simple_handler_results.pop()


def test_defaulted_hook():
    has_hooks = HasHooks()

    has_hooks.defaulted_hook += _defaulted_handler
    has_hooks.activate_defaulted_hook()

    assert len(_defaulted_handler_results) == 2
    assert _defaulted_handler_results[0][0] is has_hooks
    assert _defaulted_handler_results[0][1] == 'Test'
    assert _defaulted_handler_results[1][0] is has_hooks
    assert _defaulted_handler_results[1][1] == 'NonDefaultValue'

    while _defaulted_handler_results:
        _defaulted_handler_results.pop()


def test_cleanup():
    assert len(HasHooks.simple_hook._bound_hooks) == 0
    assert len(HasHooks.defaulted_hook._bound_hooks) == 0
