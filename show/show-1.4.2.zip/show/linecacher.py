"""Like linecache, but with support for getting lines from
interactive Python and iPython use, too."""

import sys
import linecache
from show.exceptions import ArgsUnavailable
import re

try:
    __IPYTHON__
    _IPY = True
except NameError:
    _IPY = False

isInteractive = hasattr(sys, 'ps1') or hasattr(sys, 'ipcompleter')
# see http://bit.ly/1aNuD3S

if _IPY:
    # Under IPython, want to depend on _ih mechanism to show source.
    # So acquire local access to it.
    import IPython
    ip = IPython.get_ipython()
    _ih = ip.history_manager.input_hist_parsed

    CELLRE = re.compile(r'<ipython-input-(\d+)-\w+>')

    def frame_to_source_info(frame):
        """
        Given a Python call frame, e.g. from ``inspect.currentframe()`` or any
        of its ``f_back`` predecessors, return the best filename and lineno
        combination.
        """
        return frame.f_code.co_filename, frame.f_lineno

    def getline(filename, lineno):
        if not _ih:
            return None
        m = CELLRE.match(filename)
        if not m:
            return None
        cellno = int(m.group(1))
        if not cellno:
            return None
        line = _ih[cellno].splitlines()[lineno-1]
        return line

    def find_cell_loc(frame):
        filename = frame.f_code.co_filename
        lineno = frame.f_lineno
        m = CELLRE.match(filename)
        if not m:
            return None, lineno
        cellno = int(m.group(1))
        if not cellno:
            return None, lineno
        return cellno, lineno

elif isInteractive:
    # This code is suspect. Not clear that, outside of IPython's well-structured
    # history mechanism, that interactive execution will provide the level of
    # reliable source fetching necessary.

    system = str(sys.platform).lower()

    if 'win32' in system:
        try:
            import pyreadline
            pyreadline.get_history_item
            import pyreadline as rl
        except:
            # fallback
            import readline as rl
    else:
        import readline as rl

    class History(object):
        """
        Singleton proxy for readline
        """

        def __init__(self):
            self._lines = [None]    # first item None to compensate:
                                    # 0-based arraysbut 1-based line numbers
            current_item = rl.get_history_item(rl.get_current_history_length())
            self._lines.append(current_item)
            rl.clear_history()
            self._lastseen = rl.get_current_history_length()
            # have we seen it all?

        @property
        def lines(self):
            """
            The magically self-updating lines property.
            """
            self._update()
            return self._lines

        def _update(self):
            """
            If the lines have not been recently updated (readlines knows more
            lines than we do), import those lines.
            """
            cur_hist_len = rl.get_current_history_length()
            if cur_hist_len > self._lastseen:
                for i in range(self._lastseen + 1, cur_hist_len + 1):
                    self._lines.extend(rl.get_history_item(i).splitlines())
                self._lastseen = cur_hist_len

            # Fancier splitlines() thing required because iPython stores
            # history lines for multi-line strings with embedded newlines.
            # Iteractive Python stores them individually.

        def prev(self, offset=0):
            """
            Show the previous line. Or can go back a few, with offset
            """
            return self.lines[-2 - abs(offset)]

        def clear(self):
            """
            Obliviate! Clear the history.
            """
            rl.clear_history()
            self._lines = [None]    # first item None to compensate:
                                    # 0-based arrays but 1-based line numbers
            current_item = rl.get_history_item(rl.get_current_history_length())
            self._lines.append(current_item)

        #def show(self):
        #    """
        #    Show last items.
        #    """
        #    for lineno, line in enumerate(self.lines[1:], start=1):
        #        print "{0:3}: {1}".format(lineno, line)

    history = History()

    def frame_to_source_info(frame):
        """
        Given a Python call frame, e.g. from ``inspect.currentframe()`` or any
        of its ``f_back`` predecessors, return the best filename and lineno
        combination.
        """
        filename, lineno = frame.f_code.co_filename, frame.f_lineno
        if filename.startswith(('<stdin>', '<ipython-input')):
            if lineno == 1:
                lineno = len(history.lines)
            return ('<stdin>', lineno)
        return (filename, lineno)

    def getline(filename, lineno):
        """
        Replace ``linecache.getline()`` with function that first determines if
        we need to get from history, or from a regular file.
        """
        # print "getline: filename = ", filename, "lineno = ", lineno
        if filename == '<stdin>':
            index = -1 if lineno == 1 else lineno - 1
            # for interactive Python, lineno == 1 a lot
            try:
                return history.lines[index]
            except IndexError:
                raise ArgsUnavailable('Cannot retrieve history line {index}')
        else:
            return linecache.getline(filename, lineno)

else:
    history = None
    getline = linecache.getline

    def frame_to_source_info(frame):
        """
        Given a Python call frame, e.g. from ``inspect.currentframe()`` or any
        of its ``f_back`` predecessors, return the best filename and lineno
        combination. If not running interactively, just use the Python data
        structures.
        """
        return (frame.f_code.co_filename, frame.f_lineno)
