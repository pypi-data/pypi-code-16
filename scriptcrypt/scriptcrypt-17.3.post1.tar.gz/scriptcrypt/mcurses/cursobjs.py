import curses


class column(object):
    def __init__(self):
        self.__window = None
        self.__sizeX = 0
        self.__sizeY = 0
        self.__maxX = 0
        self.__maxY = 0
        self.__bordered = True
        self.__itemOffset = 0
        self.active = False
        self.selected = 0
        self.items = []
        self.highlitedItems = set()

    def border(self, border):
        self.__bordered = border
        if self.__bordered:
            self.__window.move(1, 1)
            self.__maxY = self.__sizeY - 2
            self.__maxX = self.__sizeX - 2
        else:
            self.__window.move(0, 0)
            self.__maxY = self.__sizeY
            self.__maxX = self.__sizeX

    def window(self, window, border=True):
        self.__window = window
        self.__sizeY, self.__sizeX = self.__window.getmaxyx()
        self.border(border)

    def update(self, step):
        newPos = self.selected + step
        if newPos < self.__itemOffset:
            if newPos >= 0:
                self.__itemOffset = newPos
                self.selected = newPos
            else:
                self.__itemOffset = 0
                self.selected = 0
        elif newPos > self.__itemOffset + self.__maxY - 1:
            if newPos >= len(self.items):
                self.__itemOffset = len(self.items) - self.__maxY
                self.selected = len(self.items) - 1
            else:
                self.__itemOffset += step
                self.selected = newPos
        else:
            self.selected = newPos if newPos < \
                    len(self.items) - 1 else len(self.items) - 1

    def returnSelection(self):
        if self.selected < 0 or self.selected > (len(self.items) - 1):
            self.selected = 0
            self.__itemOffset = 0

    def draw(self):
        self.__window.erase()

        if self.__bordered:
            self.__window.box()

        if not self.items:
            return

        offset = 1 if self.__bordered else 0

        for lineNum in range(min(self.__maxY,
                                 len(self.items) - self.__itemOffset)):
            highlited = True if self.items[lineNum] in \
                    self.highlitedItems else False
            selected = True if lineNum + self.__itemOffset \
                == self.selected else False
            active = self.active
            col = curses.color_pair(2)
            if selected and active and highlited:
                col = curses.color_pair(2)
                self.__window.hline(lineNum + offset, offset, ' ',
                                    self.__maxX, col)
            elif selected and active and not highlited:
                col = curses.color_pair(3)
                self.__window.hline(lineNum + offset, offset, ' ',
                                    self.__maxX, col)
            elif selected and not active and highlited:
                col = curses.color_pair(4)
                self.__window.hline(lineNum + offset, offset, ' ',
                                    self.__maxX, col)
            elif selected and not active and not highlited:
                col = curses.color_pair(5)
                self.__window.hline(lineNum + offset, offset, ' ',
                                    self.__maxX, col)
            elif not selected and active and highlited:
                col = curses.color_pair(6)
                self.__window.hline(lineNum + offset, offset, ' ',
                                    self.__maxX, col)
            elif not selected and active and not highlited:
                col = curses.color_pair(7)
                self.__window.hline(lineNum + offset, offset, ' ',
                                    self.__maxX, col)
            elif not selected and not active and highlited:
                col = curses.color_pair(8)
                self.__window.hline(lineNum + offset, offset, ' ',
                                    self.__maxX, col)
            elif not selected and not active and not highlited:
                col = curses.color_pair(9)
                self.__window.hline(lineNum + offset, offset, ' ',
                                    self.__maxX, col)
            self.__window.addstr(lineNum + offset, offset,
                                 self.items[lineNum + self.__itemOffset]
                                 [:self.__maxX], col)
            self.__window.redrawwin()

    def windowRefresh(self):
        self.__window.refresh()
