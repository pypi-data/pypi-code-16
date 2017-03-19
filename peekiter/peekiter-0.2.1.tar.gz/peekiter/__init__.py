"""
[PeekIter]: Wrapper class for iterators, implements peeking.
"""
__VERSION = "0.2.1"
__AUTHOR = "Olian04"

class PeekIter:
    """PeekIter wrapper class, adds peek, done and next functionality to an iter.

    [iterator]: The iterator to wrap.
    [terminal]: The value to use to indicate the end of iteration.
    """
    class _Nothing:
        pass

    def __init__(self, iterator, terminal=None):
        self._iter = iter(iterator)
        self._peeked = self._Nothing()
        self._terminal = terminal
        self._terminal_reached = False

    def __repr__(self):
        return "PeekIter(done={done}, next='{next}',  \
        terminal='{terminal}', inner='{inner}')".format(
            next=self.peek,
            done=self.done,
            terminal=self.terminal,
            inner=type(self._iter))

    def __bool__(self)->bool:
        "Returns True while there are more elements available from the generator"
        return not self.done

    def __next__(self):
        return self.next

    def __iter__(self):
        "Yields every element in the iterator, then raises StopIteration."
        while not self.done:
            yield self.next
        raise StopIteration

    def _is_peeked_empty(self)->bool:
        return self._peeked and self._peeked.__class__ == self._Nothing().__class__

    @property
    def next(self):
        "Get the next value from the generator."
        if not self._is_peeked_empty():
            val, self._peeked = self._peeked, self._Nothing()
            return val
        return self._try_next()

    @property
    def peek(self):
        "Peek at the next value from the generator."
        if not self._is_peeked_empty():
            return self._peeked
        self._peeked = self._try_next()
        return self._peeked

    @property
    def done(self)->bool:
        "Returns true if the next value in the iterator is equal to the terminal_token."
        return self.peek == self.terminal

    @property
    def terminal(self):
        "Returns the terminal value"
        return self._terminal

    def _try_next(self):
        "Returns the next item from the iterator or, if that fails, returns the terminal_token."
        if self._terminal_reached:
            return self.terminal
        try:
            nv = next(self._iter)
            if nv == self.terminal:
                raise StopIteration

            return nv
        except StopIteration:
            self._terminal_reached = True
            return self.terminal

    def fork(self):
        """Forks the generator as is, i.e. in its current state.

        [WARNING]: This utelizes itertools.tee, which makes PeekIter.fork() a highly demanding operation.
        Do NOT use this operation unless absolutely nessessary.
        [WARNING]: Iterator has to be finit as of the time of the fork.
            [NOT FINIT, DUE TO INFINIT LOOP "while (true)"]:
                i = 0
                while (true):
                    yield i
                    i += 1
            [MIGHT NOT BE FINIT, DUE TO OUTER DEPENDENCY "run"]:
                i = 0
                while (run):
                    yield i
                    i += 1
        """
        from itertools import tee
        _iters = tee(self._iter)
        self._iter = _iters[0]
        ret = PeekIter(_iters[1])
        ret._peeked = self._peeked
        return ret
