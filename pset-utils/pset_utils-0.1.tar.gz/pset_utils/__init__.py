"""
A module that provides useful functionality for pyplot.

```Figure = figure_setup(pyplot)```
in an interactive shell, or
```Figure = figure_setup(pyplot, False)```
in a script, will allow you to use
```
with Figure(name, figsize=figsize) as fig:
    # plot things
```
to easily display or save plots.

To use monochromatic lines:
    pyplot.rcParams.update{'axes.prop_cycle': monochrome}

To use the same font as the host document in embeded pgf:
    pyplot.rcParams.update(pgf_params)
"""
import contextlib
from cycler import cycler

# print monochromatic lines
monochrome = (cycler('marker', ['', '.']) *
              cycler('color', ['k', '0.5']) *
              cycler('linestyle', ['-', '--', ':', '-.']))

# set up matplotlib for pgf export
pgf_params = {
        'font.family': 'serif',
        'font.serif': [],
        'font.sans-serif': [],
}

# default figure size
FIGSIZE = (6, 6)

class _Figure(contextlib.AbstractContextManager):
    """A context manager to create and display or save a figure."""

    _number = 0

    def __init__(self, name=None, *args, **kwargs):
        if name is None:
            name = self._number
            type(self)._number += 1
        self.name = name
        if 'figsize' not in kwargs:
            kwargs['figsize'] = FIGSIZE
        self.fig = self._plt.figure(*args, **kwargs)

    def __enter__(self):
        return self.fig

    def __exit__(self, *args):
        if self._interactive:
            self._plt.show()
        else:
            self.fig.savefig(self.name)
            self._plt.close(self.fig)


def figure_setup(pyplot, interactive=True):
    """Returns a context manager for displaying or saving figures.

    Args:
        pyplot: The pyplot module
        interactive (optional): If true (default), this is being run from an
            interactive shell, and the context manager will display the figure
            upon exiting.  Otherwise, the figure will be saved upon exiting.

    Returns:
        A context manager for displaying or saving figures.
    """
    _Figure._plt = pyplot
    _Figure._interactive = interactive
    return _Figure

