"""Tests for runaway."""


# [ Imports ]
# [ -Python ]
import types
import typing
# [ -Third party ]
import utaw
# [ -Project ]
from .runaway import CoroAction, run


# pylint: disable=fixme
# XXX simplify/extract/abstract to improve clarity
# XXX tighten types
# pylint: enable=fixme


# [ Helpers ]
def double(value: int, _: bool) -> typing.Tuple[int, CoroAction]:
    """Return double the value."""
    return 2 * value, CoroAction.SEND


def two_to_four(func: typing.Callable) -> typing.Callable:
    """Convert a transform from two to four values."""
    def wrapper(
        signal: typing.Any,
        is_error: bool,
        source_coro: typing.Any,
        scheduler_state: typing.Any
    ) -> typing.Tuple[typing.Any, CoroAction, typing.Any, typing.Any]:
        """Wrap a two-arg transform with a 4 arg transform."""
        if is_error and isinstance(signal, StopIteration):
            return signal.value, CoroAction.RETURN, None, scheduler_state
        signal, action = func(signal, is_error)
        return signal, action, source_coro, scheduler_state
    return wrapper


# [ Tests ]
def test_run_empty_coroutine_without_return() -> None:
    """
    Test running an empty coroutine without a return.

    Expect a return of 'None'.
    """
    # Given
    @types.coroutine
    def empty_coroutine_without_return() -> typing.Generator:
        """An empty coroutine with no return."""
        yield from tuple()

    # When
    result = run(empty_coroutine_without_return())

    # Then
    utaw.assertIsNone(result)


def test_run_empty_coroutine_with_return() -> None:
    """
    Test running an empty coroutine with a return.

    Expect the sentinel to be returned.
    """
    # Given
    sentinel = object()

    @types.coroutine
    def empty_coroutine_with_return() -> typing.Generator:
        """An empty coroutine with a return."""
        yield from tuple()
        return sentinel

    # When
    result = run(empty_coroutine_with_return())

    # Then
    utaw.assertIs(result, sentinel)


def test_run_non_empty_coroutine_without_return() -> None:
    """
    Test running a non-empty coroutine without a return.

    Expect a return of 'None'.
    """
    # Given
    @types.coroutine
    def non_empty_coro_without_return() -> typing.Generator:
        """A non-empty coroutine with no return."""
        for value in (1, 2, 3):
            yield value

    # When
    result = run(non_empty_coro_without_return())

    # Then
    utaw.assertIsNone(result)


def test_run_non_empty_coroutine_with_return() -> None:
    """
    Test running a non-empty coroutine with a return.

    Expect doubled values to be returned.
    """
    # Given
    values_to_yield = [1, 2, 3, 4]
    expected_return = [2, 4, 6, 8]

    @types.coroutine
    def non_empty_coroutine_with_return() -> typing.Generator:
        """A non-empty coroutine with a return."""
        return_value = []
        for value in values_to_yield:
            sent_value = yield value
            return_value.append(sent_value)
        return return_value

    # When
    result = run(non_empty_coroutine_with_return(), transform=two_to_four(double))

    # Then
    utaw.assertListEqual(result, expected_return)


def test_run_empty_native_coroutine_without_return() -> None:
    """
    Test running an empty native coroutine without a return.

    Expect a return of 'None'.
    """
    # Given
    async def empty_native_coro_without_return() -> None:
        """An empty native coroutine with no return."""
        pass

    # When
    result = run(empty_native_coro_without_return())

    # Then
    utaw.assertIsNone(result)


def test_run_empty_native_coroutine_with_return() -> None:
    """
    Test running an empty native coroutine with a return.

    Expect the sentinel to be returned.
    """
    # Given
    sentinel = object()

    async def empty_native_coroutine_with_return() -> object:
        """An empty native coroutine with a return."""
        return sentinel

    # When
    result = run(empty_native_coroutine_with_return())

    # Then
    utaw.assertIs(result, sentinel)


def test_run_non_empty_native_coroutine_without_return() -> None:
    """
    Test running a non-empty native coroutine without a return.

    Expect a return of 'None'.
    """
    # Given
    @types.coroutine
    def non_empty_coro_without_return() -> typing.Generator:
        """A non-empty coroutine with no return."""
        for value in (1, 2, 3):
            yield value

    async def non_empty_native_coro_without_return() -> None:
        """A non-empty coro with no return."""
        await non_empty_coro_without_return()

    # When
    result = run(non_empty_native_coro_without_return())

    # Then
    utaw.assertIsNone(result)


def test_run_non_empty_native_coroutine_with_return() -> None:
    """
    Test running a non-empty native coroutine with a return.

    Expect doubled values to be returned.
    """
    # Given
    values_to_yield = [1, 2, 3, 4]
    expected_return = [2, 4, 6, 8]

    @types.coroutine
    def non_empty_coroutine_with_return() -> typing.Generator:
        """A non-empty coroutine with a return."""
        return_value = []
        for value in values_to_yield:
            sent_value = yield value
            return_value.append(sent_value)
        return return_value

    async def non_empty_native_coro_with_return() -> None:
        """A non-empty coro with a return."""
        return await non_empty_coroutine_with_return()

    # When
    result = run(non_empty_native_coro_with_return(), transform=two_to_four(double))

    # Then
    utaw.assertListEqual(result, expected_return)


def test_run_empty_async_generator_without_return() -> None:
    """
    Test running an empty async generator without a return.

    Expect a return of 'None'.
    """
    # Given
    async def empty_async_generator() -> typing.AsyncIterator:
        """An empty async generator with no return."""
        empty_list = []  # type: typing.List
        for item in empty_list:
            yield item  # pylint: disable=yield-inside-async-function

    async def run_generator_without_return() -> None:
        """Run an async generator."""
        async for _ in empty_async_generator():  # noqa: F841
            pass

    # When
    result = run(run_generator_without_return())

    # Then
    utaw.assertIsNone(result)


def test_run_empty_async_generator_with_return() -> None:
    """
    Test running an empty async generator with a return.

    Expect the sentinel to be returned.
    """
    # Given
    sentinel = object()

    async def empty_async_generator() -> typing.AsyncIterator:
        """An empty async generator with no return."""
        empty_list = []  # type: typing.List
        for item in empty_list:
            yield item  # pylint: disable=yield-inside-async-function

    async def run_generator_with_return() -> object:
        """Run an async generator."""
        async for _ in empty_async_generator():  # noqa: F841
            pass
        return sentinel

    # When
    result = run(run_generator_with_return())

    # Then
    utaw.assertIs(result, sentinel)


def test_run_non_empty_async_generator_without_return() -> None:
    """
    Test running a non-empty async generator without a return.

    Expect a return of 'None'.
    """
    # Given
    async def non_empty_async_generator() -> typing.AsyncIterator:
        """A non-empty async generator with no return."""
        for item in [1, 2, 3, 4]:
            yield item  # pylint: disable=yield-inside-async-function

    async def run_generator_without_return() -> None:
        """Run an async generator."""
        async for _ in non_empty_async_generator():  # noqa: F841
            pass

    # When
    result = run(run_generator_without_return())

    # Then
    utaw.assertIsNone(result)


def test_run_non_empty_async_generator_with_return() -> None:
    """
    Test running a non-empty async generator with a return.

    Expect the input values to be doubled.
    """
    # Given
    values_to_yield = [1, 2, 3, 4]
    expected_return = [2, 4, 6, 8]

    @types.coroutine
    def coro_transform(item: typing.Any) -> typing.Any:
        """Offer the item up to a coroutine, and return what it sends back."""
        to_return = yield item
        return to_return

    async def non_empty_async_generator() -> typing.AsyncIterator:
        """A non-empty async generator with no return."""
        for item in values_to_yield:
            # yield something that has to be awaited, or you're just
            # looping through - might as well return a list.
            yield await coro_transform(item)  # pylint: disable=yield-inside-async-function

    async def run_generator_with_return() -> object:
        """Run an async generator."""
        return_values = []  # type: typing.List[int]
        async for yielded_value in non_empty_async_generator():
            return_values.append(yielded_value)
        return return_values

    # When
    result = run(run_generator_with_return(), transform=two_to_four(double))

    # Then
    utaw.assertListEqual(result, expected_return)


def test_run_and_break_async_generator_without_return() -> None:
    """
    Test running and breaking out of a non-empty async generator without a return.

    Expect None.
    """
    # Given
    values_to_yield = [1, 2, 3, 4]

    @types.coroutine
    def coro_transform(item: typing.Any) -> typing.Any:
        """Offer the item up to a coroutine, and return what it sends back."""
        to_return = yield item
        return to_return

    async def non_empty_async_generator() -> typing.AsyncIterator:
        """A non-empty async generator with no return."""
        for item in values_to_yield:
            # yield something that has to be awaited, or you're just
            # looping through - might as well return a list.
            yield await coro_transform(item)  # pylint: disable=yield-inside-async-function

    async def run_generator_without_return() -> None:
        """Run an async generator."""
        async for yielded_value in non_empty_async_generator():
            if yielded_value == 2:
                break

    # When
    result = run(run_generator_without_return(), transform=two_to_four(double))

    # Then
    utaw.assertIsNone(result)


def test_run_and_break_async_generator_with_return() -> None:
    """
    Test running and breaking out of a non-empty async generator witha return.

    Expect the input values to be doubled.
    """
    # Given
    values_to_yield = [1, 2, 3, 4]
    expected_return = [2]

    @types.coroutine
    def coro_transform(item: typing.Any) -> typing.Any:
        """Offer the item up to a coroutine, and return what it sends back."""
        to_return = yield item
        return to_return

    async def non_empty_async_generator() -> typing.AsyncIterator:
        """A non-empty async generator with no return."""
        for item in values_to_yield:
            # yield something that has to be awaited, or you're just
            # looping through - might as well return a list.
            yield await coro_transform(item)  # pylint: disable=yield-inside-async-function

    async def run_generator_with_return() -> typing.List[int]:
        """Run an async generator."""
        return_values = []
        async for yielded_value in non_empty_async_generator():
            return_values.append(yielded_value)
            if yielded_value == 2:
                break
        return return_values

    # When
    result = run(run_generator_with_return(), transform=two_to_four(double))

    # Then
    utaw.assertListEqual(result, expected_return)


def test_run_and_break_async_generator_with_catch_generator_exit() -> None:
    """
    Test running and breaking out of a non-empty async generator.

    Catch the generator exit.

    Expect the input values to be doubled, and expect the finally to be run.
    """
    # Given
    values_to_yield = [1, 2, 3, 4]
    expected_return = [2]
    doubled_values = []
    expected_doubled_values = [1, 100]

    @types.coroutine
    def coro_transform(item: typing.Any) -> typing.Any:
        """Offer the item up to a coroutine, and return what it sends back."""
        to_return = yield item
        return to_return

    async def non_empty_async_generator() -> typing.AsyncIterator:
        """A non-empty async generator with no return."""
        try:
            for item in values_to_yield:
                # yield something that has to be awaited, or you're just
                # looping through - might as well return a list.
                yield await coro_transform(item)  # pylint: disable=yield-inside-async-function
        except GeneratorExit:
            # cleanup
            await coro_transform(100)

    async def run_generator_with_return() -> typing.List[int]:
        """Run an async generator."""
        return_values = []
        async for yielded_value in non_empty_async_generator():
            return_values.append(yielded_value)
            if yielded_value == 2:
                break
        return return_values

    def append_double(value: int, _: bool) -> typing.Tuple[int, CoroAction]:
        """Return double the value."""
        doubled_values.append(value)
        return 2 * value, CoroAction.SEND

    # When
    result = run(run_generator_with_return(), transform=two_to_four(append_double))

    # Then
    utaw.assertListEqual(result, expected_return)
    utaw.assertListEqual(doubled_values, expected_doubled_values)


def test_run_with_transformation_error() -> None:
    """
    Test an error in the transformation.

    Expect the error to be propagated up to the runner's caller.
    """
    # Given
    values_to_yield = [1, 2, 3, 4]

    @types.coroutine
    def non_empty_coroutine_with_return() -> typing.Generator:
        """A non-empty coroutine with a return."""
        return_value = []
        for value in values_to_yield:
            try:
                sent_value = yield value
            except RuntimeError as the_error:
                return the_error
            return_value.append(sent_value)
        return return_value

    def error(from_coro: typing.Any, is_error: bool) -> typing.Tuple[typing.Any, bool]:  # pylint: disable=unused-argument
        """Raise an error."""
        raise RuntimeError("raised on purpose")

    # Then
    with utaw.assertRaises(RuntimeError):
        # When
        run(non_empty_coroutine_with_return(), transform=two_to_four(error))


def test_return_error_from_transform() -> None:
    """
    Test an error returned from the transformation.

    Expect the error to be sent into the coro..
    """
    # Given
    values_to_yield = [1, 2, 3, 4]
    expected_error_type = RuntimeError
    expected_error_args = ("raised on purpose",)

    @types.coroutine
    def non_empty_coroutine_with_return() -> typing.Generator:
        """A non-empty coroutine with a return."""
        return_value = []
        for value in values_to_yield:
            try:
                sent_value = yield value
            except RuntimeError as the_error:
                return the_error
            return_value.append(sent_value)
        return return_value

    def return_error(from_coro: typing.Any, is_error: bool) -> typing.Tuple[Exception, CoroAction]:  # pylint: disable=unused-argument
        """Return an error."""
        return RuntimeError("raised on purpose"), CoroAction.THROW

    # When
    result = run(non_empty_coroutine_with_return(), transform=two_to_four(return_error))

    # Then
    utaw.assertIsInstance(result, expected_error_type)
    utaw.assertTrue(hasattr(result, 'args'))
    utaw.assertTupleEqual(result.args, expected_error_args)  # pylint: disable=no-member
    # pylint is unhappy about the args attr, but we just asserted it's there.


def test_run_with_coro_error() -> None:
    """
    Test a coro which raises an error.

    Expect transform to receive the error.
    """
    # Given
    values_to_yield = [1, 2, 3, 4]
    transform_received_error = None
    expected_error_type = RuntimeError
    expected_error_args = ('from within coro',)

    @types.coroutine
    def non_empty_coroutine_with_return() -> typing.Generator:
        """A non-empty coroutine with a return."""
        return_value = []  # type: typing.List[int]
        for value in values_to_yield:
            yield value
            raise RuntimeError('from within coro')
        return return_value

    def error_double(value: typing.Union[int, Exception], is_error: bool) -> typing.Tuple[int, CoroAction]:
        """Return double the value."""
        nonlocal transform_received_error
        if is_error and isinstance(value, Exception):
            transform_received_error = value
            raise value
        elif isinstance(value, int):
            return 2 * value, CoroAction.SEND
        else:
            raise RuntimeError('bad value passed to double ({})'.format(value))

    # When
    try:
        run(non_empty_coroutine_with_return(), transform=two_to_four(error_double))
    except RuntimeError as error:
        if 'from within coro' in str(error):
            pass
        else:
            raise

    # Then
    utaw.assertIsInstance(transform_received_error, expected_error_type)
    utaw.assertTupleEqual(transform_received_error.args, expected_error_args)


def test_run_with_native_coro_error() -> None:
    """
    Test running an empty native coroutine that raises an error.

    Expect the transform to receive the error.
    """
    # Given
    transform_received_error = None
    expected_error_type = RuntimeError
    expected_error_args = ('from within native coro',)

    async def raise_error() -> None:
        """Raise an error."""
        raise RuntimeError('from within native coro')

    def relay_error(value: Exception, _: bool) -> typing.Tuple[None, bool]:
        """Raise received error."""
        nonlocal transform_received_error
        transform_received_error = value
        raise value

    # When
    try:
        run(raise_error(), two_to_four(relay_error))
    except RuntimeError as error:
        if 'from within native coro' in str(error):
            pass
        else:
            raise

    # Then
    utaw.assertIsInstance(transform_received_error, expected_error_type)
    utaw.assertTupleEqual(transform_received_error.args, expected_error_args)


def test_run_with_async_gen_error() -> None:
    """
    Test running an async generator which raises.

    Expect the transform to receive the error.
    """
    # Given
    values_to_yield = [1, 2, 3, 4]
    transform_received_error = None
    expected_error_type = RuntimeError
    expected_error_args = ('from within async generator',)

    @types.coroutine
    def coro_transform(item: typing.Any) -> typing.Any:
        """Offer the item up to a coroutine, and return what it sends back."""
        raise RuntimeError('from within async generator')
        to_return = yield item  # pylint: disable=unreachable
        return to_return

    async def non_empty_async_generator() -> typing.AsyncIterator:
        """A non-empty async generator with no return."""
        for item in values_to_yield:
            # yield something that has to be awaited, or you're just
            # looping through - might as well return a list.
            yield await coro_transform(item)  # pylint: disable=yield-inside-async-function

    async def run_generator_with_return() -> object:
        """Run an async generator."""
        return_values = []  # type: typing.List[int]
        async for yielded_value in non_empty_async_generator():
            return_values.append(yielded_value)
        return return_values

    def relay_error(value: Exception, _: bool) -> typing.Tuple[None, bool]:
        """Raise received error."""
        nonlocal transform_received_error
        transform_received_error = value
        raise value

    # When
    try:
        run(run_generator_with_return(), transform=two_to_four(relay_error))
    except RuntimeError as error:
        if 'from within async generator' in str(error):
            pass
        else:
            raise

    # Then
    utaw.assertIsInstance(transform_received_error, expected_error_type)
    utaw.assertTupleEqual(transform_received_error.args, expected_error_args)


def test_run_with_a_concurrent_transformer() -> None:
    """
    Test running with a concurrent transformer.

    Expect values from concurrent coroutines to be run interleaved.
    """
    # Given
    expected_return = [
        0, 10, 1, 100, 11, 2, 101, 12, 3, 102, 13, 4, 103, 14, 5, 104, 15, 6,
        16, 7, 17, 8, 18, 9, 19,
    ]

    @types.coroutine
    def spawn(coro: typing.Any) -> typing.Generator:
        """Spawn a coro."""
        yield {
            'command': 'spawn',
            'coro': coro,
        }

    @types.coroutine
    def send(value: typing.Any) -> typing.Generator:
        """Send a value up to the scheduler."""
        yield value

    async def counter(start: int, stop: int) -> None:
        """A counter coro."""
        for value in range(start, stop):
            await send(value)

    async def spawning_coro() -> None:
        """A coro that spawns a few other coros."""
        await spawn(counter(0, 10))
        await spawn(counter(10, 20))
        await spawn(counter(100, 105))

    def transform(
        signal: typing.Any,
        is_error: bool,
        source_coro: typing.Any,
        scheduler_state: typing.Any
    ) -> typing.Tuple[typing.Any, CoroAction, typing.Any, typing.Any]:
        """Transform the input."""
        if 'source_coro' not in scheduler_state:
            scheduler_state['source_coro'] = source_coro
        coros = scheduler_state.get('coros', [])
        scheduler_state['coros'] = coros
        if isinstance(signal, dict):
            if signal['command'] == 'spawn':
                coros.append(source_coro)
                # send initial start command into the new coro
                return None, CoroAction.SEND, signal['coro'], scheduler_state
        if is_error and isinstance(signal, StopIteration):
            # not adding it back in - it's dead
            if not coros:
                return scheduler_state.get('return', []), CoroAction.RETURN, None, scheduler_state
        else:
            coros.append(source_coro)
            # add yielded value to the eventual return list
            # this isn't meaningful, but it helps us test that
            # in fact, multiple coros were run concurrently
            to_return = scheduler_state.get('return', [])
            to_return.append(signal)
            scheduler_state['return'] = to_return
        sink_coro = coros[0]
        del coros[0]
        return None, CoroAction.SEND, sink_coro, scheduler_state

    # When
    result = run(spawning_coro(), transform=transform, state={})

    # Then
    utaw.assertListEqual(result, expected_return)


def test_ping_pong() -> None:
    """Test a ping-pong coroutine scenario."""
    # Given
    game_log = []
    expected_final_log = [
        'started',
        'ping', 'pong',
        'ping', 'pong',
        'ping', 'pong',
        'ping', 'pong',
        'ping', 'pong',
        'stopped'
    ]

    async def ping(times: int) -> None:
        """Log a ping."""
        for _ in range(times):
            await call('log', 'ping')

    async def pong(times: int) -> None:
        """Log a pong."""
        for _ in range(times):
            await call('log', 'pong')

    async def game() -> None:
        """Log a game."""
        await call('log', 'started')
        times = 5
        await concurrent(ping(times), pong(times))
        await call('log', 'stopped')

    @types.coroutine
    def call(func_name: str, *args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        """Yield a signal for a call."""
        yield {
            'signal': 'call',
            'func_name': func_name,
            'args': args,
            'kwargs': kwargs
        }

    @types.coroutine
    def concurrent(*awaitables: typing.Awaitable) -> typing.Any:
        """Yield a signal for a concurrent run."""
        yield {
            'signal': 'concurrent',
            'awaitables': awaitables
        }

    def pop_coro(state: typing.Any) -> typing.Tuple[typing.Any, CoroAction, typing.Any, typing.Any]:
        """Pop the next coro off the state."""
        next_coro = state['coros'][0]
        del state['coros'][0]
        coro = next_coro['coro']
        if 'send' in next_coro:
            action = CoroAction.SEND
            value = next_coro['send']
        elif 'throw' in next_coro:
            action = CoroAction.THROW
            value = next_coro['throw']
        else:
            action = CoroAction.CLOSE
            value = None
        return value, action, coro, state

    def log(action: str) -> None:
        """Log an action."""
        game_log.append(action)
        print(action)
        import time
        time.sleep(0.5)

    call_map = {
        'log': log
    }

    def transform_call(signal: typing.Any, coro: typing.Any, state: typing.Any) -> typing.Tuple[typing.Any, CoroAction, typing.Any, typing.Any]:
        """Transform the call."""
        call_map[signal['func_name']](*signal['args'], **signal['kwargs'])
        state['coros'].append({'coro': coro, 'send': None})
        return pop_coro(state)

    def transform_concurrent(signal: typing.Any, coro: typing.Any, state: typing.Any) -> typing.Tuple[typing.Any, CoroAction, typing.Any, typing.Any]:
        """Transform a concurrent signal."""
        for awaitable in signal['awaitables']:
            state['coros'].append({'coro': awaitable, 'send': None})
        state['waiting'].append({
            'coro': coro, 'for': list(signal['awaitables'])
        })
        return pop_coro(state)

    def transform_error(error: typing.Any, coro: typing.Any, state: typing.Any) -> typing.Tuple[typing.Any, CoroAction, typing.Any, typing.Any]:
        """Transform an error signal."""
        for waiting in state['waiting']:
            if coro in waiting['for']:
                waiting['for'].remove(coro)
                if not waiting['for']:
                    state['waiting'].remove(waiting)
                    state['coros'].append({
                        'coro': waiting['coro'], 'send': None
                    })
                return pop_coro(state)
        if not state['coros']:
            if isinstance(error, StopIteration):
                return error.value, CoroAction.RETURN, None, state
            else:
                raise error
        raise RuntimeError("Invalid branch reached.")

    signal_map = {
        'call': transform_call,
        'concurrent': transform_concurrent,
        'error': transform_error,
    }

    def transform(signal: typing.Any, is_error: bool, coro: typing.Any, state: typing.Any) -> typing.Tuple[typing.Any, CoroAction, typing.Any, typing.Any]:
        """Transform the signals into new calls."""
        if is_error:
            return signal_map['error'](signal, coro, state)  # type: ignore
        return signal_map[signal['signal']](signal, coro, state)  # type: ignore

    # When
    run(game(), transform, {'coros': [], 'waiting': []})

    # Then
    utaw.assertListEqual(game_log, expected_final_log)
