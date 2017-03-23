"""Line prefixers. Or suffixers, if you read RTL. """

class numberer(object):

    """
    A class-based factory for numbering generators. Rather like Python 2's
    ``xrange`` (or Python 3's ``range``), but intended to number lines in a file
    so it uses natural numbers starting at 1, not the typical Python 'start at
    0'. Also, returns formatted strings, not integers. Improves on what's
    possible as a functional generator on numberer because it can compute and
    return its own length.
    """

    def __init__(self, start=1, template="{n:>3}: ", length=None):
        """
        Make a numberer.
        """
        self.n = start
        self.template = template
        self.length = None
        self._formatted = None

    def __next__(self):
        """
        Return the next numbered template.
        """
        t = self.template
        result = t.format(n=self.n) if self._formatted is None else self._formatted
        self._formatted = None
        self.n += 1
        return result

    next = __next__   # for Python 2

    def __len__(self):
        """
        What is the string length of the instantiated template now? NB This can change
        over time, as n does. Fixed-width format strings limit how often it can change
        (to when n crosses a power-of-10 boundary > the fixed template length
        can accomodate). This implementation saves the templated string its has created
        for reuse. If self.length is set, however, this computation is not done, and
        self.length is assumed to be the right answer.
        """
        if self.length is not None:
            return self.length
        else:
            t = self.template
            result = t.format(n=self.n)
            self._formatted = result
            return len(result)


def first_rest(first, rest):
    """
    Line prefixer (or suffixer) that gives one string for the first line, and
    an alternate string for every subsequent line. For implementing schemes
    like the Python REPL's '>>> ' followed by '... '.
    """
    yield first
    while True:
        yield rest
