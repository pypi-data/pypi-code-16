"""Runaway module."""


# pylint: disable=fixme
# XXX build a hello-world with an example transform
# XXX what if the transform performs a close/send/throw?
# maybe actual coro objects are managed outside of transform?  Want to provide
# a common/correct/consistent interface to coros.
# in that case, how does one close a coro?  need tests for that, too
# XXX tighten types
# XXX simplify/extract/abstract to improve clarity
# XXX build a plugin/middleware-enabled transform & hello-world
# XXX test for closing a coro
# XXX enable passing type/val/tb in throw
# pylint: enable=fixme


# [ Imports ]
import enum
import sys
import typing


# [ Helpers ]
class CoroAction(enum.Enum):
    """Valid Coroutine actions."""

    SEND = 1
    THROW = 2
    CLOSE = 3
    RETURN = 4


def _default_transform(
    signal: typing.Any,
    is_error: bool,
    source_coro: typing.Any,
    scheduler_state: typing.Any
) -> typing.Tuple[typing.Any, CoroAction, typing.Any, typing.Any]:
    """
    Default transform function.

    Raises stop-iteration, but otherwise is a pass-through.
    """
    if is_error and isinstance(signal, StopIteration):
        return signal.value, CoroAction.RETURN, None, scheduler_state
    return signal, CoroAction.SEND, source_coro, scheduler_state


# [ API ]
def run(
    coro: typing.Any,
    transform: typing.Callable[
        [typing.Any, bool, typing.Any, typing.Any],
        typing.Tuple[typing.Any, CoroAction, typing.Any, typing.Any]
    ]=_default_transform,
    state: typing.Any=None
) -> typing.Any:
    """Run the given coroutine."""
    # initial input to kick things off.
    to_coro = None
    coro_action = CoroAction.SEND

    # loop
    def _run_finalizer(async_generator: typing.AsyncIterator) -> None:
        """Finalize the generator."""
        run(async_generator.aclose(), transform=transform)  # type: ignore

    try:
        old_hooks = sys.get_asyncgen_hooks()  # type: ignore
        sys.set_asyncgen_hooks(finalizer=_run_finalizer)  # type: ignore
        while True:
            try:
                # Run the coro till a yield
                if coro_action is CoroAction.THROW:
                    from_coro = coro.throw(to_coro)
                elif coro_action is CoroAction.SEND:
                    from_coro = coro.send(to_coro)
                elif coro_action is CoroAction.CLOSE:
                    from_coro = coro.close()
                elif coro_action is CoroAction.RETURN:
                    return to_coro
                else:
                    raise RuntimeError("Invalid coro action passed: {}".format(coro_action))
            except Exception as error:  # pylint: disable=broad-except
                # necessarily broad except - we're passing this back into the coro
                from_coro = error
                from_coro_is_error = True
            else:
                from_coro_is_error = False
            # transform the yielded value and send back into the coro
            to_coro, coro_action, coro, state = transform(from_coro, from_coro_is_error, coro, state)

    finally:
        sys.set_asyncgen_hooks(*old_hooks)  # type: ignore
