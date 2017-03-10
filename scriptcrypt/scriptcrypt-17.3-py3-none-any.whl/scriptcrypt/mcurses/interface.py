import curses
import scriptcrypt.db as mydb
import scriptcrypt.mcurses.cursobjs as MyCurses
from scriptcrypt.tmpfl import External
import scriptcrypt.vars as mvars
import scriptcrypt.envars as envars
from sys import stdout, exit


import locale
locale.setlocale(locale.LC_ALL, "")


class TUI(object):
    LOCAL_ENCODING = None
    PAGER = "less"
    EDITOR = "nano"
    SHELL = "sh"
    APPDIR = "~/Applications"

    def __init__(self, DB_URI):
        self.LOCAL_ENCODING = locale.getpreferredencoding()
        self.db = mydb.dbHandler(DB_URI)
        self.db.create()

    def setup(self, stdscr):
        self.stdscr = stdscr
        try:
            curses.curs_set(0)
        except:
            pass

        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_WHITE, -1)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_YELLOW)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_GREEN)
        curses.init_pair(4, curses.COLOR_CYAN, -1)
        curses.init_pair(5, curses.COLOR_GREEN, -1)
        curses.init_pair(6, curses.COLOR_YELLOW, -1)
        curses.init_pair(7, curses.COLOR_WHITE, -1)
        curses.init_pair(8, curses.COLOR_YELLOW, -1)
        curses.init_pair(9, curses.COLOR_WHITE, -1)

        self.bodyInfo = MyCurses.column()
        self.bodyInfo.selected = -1
        self.bodyCat = MyCurses.column()
        self.bodySub = MyCurses.column()
        self.bodyEnt = MyCurses.column()
        self.bodyEnt.active = True
        self.winEdit = MyCurses.column()
        self.winEdit.active = True
        self.column = 2

        self.stdscr.nodelay(0)

        self.setupAndDrawScreen()
        self.refreshBody()
        self.run()

    def setupAndDrawScreen(self):
        self.maxY, self.maxX = self.stdscr.getmaxyx()
        self.headWin = curses.newwin(1, self.maxX, 0, 0)
        self.bodyWin = curses.newwin(self.maxY - 2, self.maxX, 1, 0)
        self.bodyMaxY, self.bodyMaxX = self.bodyWin.getmaxyx()
        self.footerWin = curses.newwin(1, self.maxX, self.maxY - 1, 0)

        self.stdscr.timeout(100)
        self.bodyWin.keypad(1)
        self.bodyWin.noutrefresh()
        curses.doupdate()

        self.drawHead()

    def drawHead(self):
        info = self.db.dbURI[10:]
        self.headWin.addstr(0, 1, info[:self.maxX - 2], curses.color_pair(3))
        self.headWin.bkgd(' ', curses.color_pair(3))
        self.headWin.noutrefresh()

    def drawFooter(self, string):
        self.footerWin.erase()
        self.footerWin.addstr(0, 1, string[:self.maxX - 2],
                              curses.color_pair(3))
        self.footerWin.bkgd(' ', curses.color_pair(3))
        self.footerWin.noutrefresh()

    def refreshBody(self):
        if len(self.db.entryNames()) == 0 or\
              len(self.db.categoryNames()) == 0 or\
              len(self.db.subcategoryNames()) == 0:
            self.flashText(mvars.populateMessage)
            self.addEntry()
            if len(self.db.entryNames()) == 0 or\
                    len(self.db.categoryNames()) == 0 or\
                    len(self.db.subcategoryNames()) == 0:
                exit()

        self.drawFooter(mvars.footerMenu)
        self.bodyWin.erase()
        self.bodyWin.move(1, 1)
        self.bodyInfo.window(self.bodyWin.subwin(4, self.bodyMaxX - 2, 1, 1),
                             False)
        self.bodyCat.window(self.bodyWin.subwin(self.bodyMaxY - 3,
                                                self.bodyMaxX // 3,
                                                4,
                                                0))
        self.bodySub.window(self.bodyWin.subwin(self.bodyMaxY - 3,
                                                self.bodyMaxX // 3,
                                                4,
                                                self.bodyMaxX // 3))
        self.bodyEnt.window(self.bodyWin.subwin(self.bodyMaxY - 3,
                                                self.bodyMaxX // 3,
                                                4, 2 * self.bodyMaxX // 3))

        self.bodyCat.items = self.db.categoryNames()
        self.bodyCat.returnSelection()
        category = self.bodyCat.items[self.bodyCat.selected]
        self.bodySub.items = self.db.categorySubcategories(category)
        self.bodySub.returnSelection()
        subcategory = self.bodySub.items[self.bodySub.selected]
        self.bodyEnt.items = self.db.categorySubcategoryEntries(category,
                                                                subcategory)
        self.bodyEnt.returnSelection()
        name = self.bodyEnt.items[self.bodyEnt.selected]
        info = self.db.entryInfo(name)
        self.bodyInfo.items = ["Name: " + info["name"],
                               "Description: " + info["description"],
                               info["description"][self.maxX - 15:]]

        self.bodyInfo.draw()
        self.bodyCat.draw()
        self.bodySub.draw()
        self.bodyEnt.draw()

        self.bodyWin.refresh()

    def addEntry(self):
        self.winEdit.highlitedItems.update("a")
        self.winEdit.items = ["Name: ",
                              "Category: ",
                              "Subcategory: ",
                              "Description: ",
                              mvars.scriptMessage,
                              mvars.scriptMessage]
        self.winEdit.selected = 0
        self.runEdit()

    def modEntry(self):
        items = self.db.entryInfo(self.bodyEnt.items[self.bodyEnt.selected])
        self.winEdit.items = ["Name: " + items["name"],
                              "Category: " + items["category"],
                              "Subcategory: " + items["subcategory"],
                              "Description: " + items["description"],
                              items["scriptInst"],
                              items["scriptUinst"]]
        self.winEdit.selected = 0
        self.runEdit()

    def __applyChanges(self):
        if len(self.winEdit.items[1]) <= 10:
            self.winEdit.items[1] = "Category: [Empty]"
        if len(self.winEdit.items[2]) <= 13:
            self.winEdit.items[2] = "Subcategory: [Empty]"
        if "a" in self.winEdit.highlitedItems:
            self.winEdit.highlitedItems.clear()
            self.db.addEntry({"name": self.winEdit.items[0][6:],
                              "category": self.winEdit.items[1][10:],
                              "subcategory": self.winEdit.items[2][13:],
                              "description": self.winEdit.items[3][13:],
                              "scriptInst": self.winEdit.items[4],
                              "scriptUinst": self.winEdit.items[5]})

        else:
            self.db.editEntry(self.bodyEnt.items[self.bodyEnt.selected],
                              {"name": self.winEdit.items[0][6:],
                               "category": self.winEdit.items[1][10:],
                               "subcategory": self.winEdit.items[2][13:],
                               "description": self.winEdit.items[3][13:],
                               "scriptInst": self.winEdit.items[4],
                               "scriptUinst": self.winEdit.items[5]})

    def drawEditWin(self):
        self.bodyWin.erase()
        self.drawFooter(mvars.footerEdit)
        self.winEdit.window(self.bodyWin.subwin(self.bodyMaxY,
                                                self.bodyMaxX,
                                                1, 0))
        tempIns = self.winEdit.items[4]
        tempUns = self.winEdit.items[5]
        self.winEdit.items[4] = "Install script"
        self.winEdit.items[5] = "Uninstall script"
        self.winEdit.draw()
        self.bodyWin.refresh()
        self.winEdit.items[4] = tempIns
        self.winEdit.items[5] = tempUns

    def __queryString(self, text):
        self.bodyWin.erase()
        self.drawFooter("")
        window = self.bodyWin.subwin(self.bodyMaxY, self.bodyMaxX, 1, 0)
        curses.echo()
        curses.curs_set(1)
        window.addstr(1, 1, text)
        strg = self.bodyWin.getstr(2, 1)
        try:
            strg = strg.decode(self.LOCAL_ENCODING)
        except:
            strg = ""
        curses.noecho()
        curses.curs_set(0)
        return strg

    def rmEntry(self):
        if not self.bodyEnt.highlitedItems:
            return

        self.bodyWin.erase()
        self.bodyWin.addstr(1, 1, 'Remove entries?(y/n)', curses.color_pair(3))
        winList = MyCurses.column()
        winList.window(self.bodyWin.subwin(self.bodyMaxY - 4,
                                           self.bodyMaxX - 2,
                                           4,
                                           1), False)
        winList.items = list(self.bodyEnt.highlitedItems)
        winList.selected = -1
        winList.draw()
        self.bodyWin.refresh()
        c = self.bodyWin.getch()
        if c == ord("y") or c == ord("Y"):
            for item in winList.items:
                self.db.rmEntry(item)
            self.bodyEnt.highlitedItems.clear()

    def cursesExit(self):
        curses.savetty()
        curses.endwin()

    def cursesReturn(self):
        self.stdscr = curses.initscr()
        curses.resetty()

    def flashText(self, text):
        self.bodyWin.erase()
        winList = MyCurses.column()
        winList.window(self.bodyWin.subwin(self.bodyMaxY - 2,
                                           self.bodyMaxX - 2,
                                           2,
                                           1), False)
        winList.items = list(text.split('\n'))
        winList.selected = -1
        winList.draw()
        self.bodyWin.refresh()
        self.bodyWin.getch()

    def run(self):
        self.refreshBody()
        while True:
            try:
                c = self.bodyWin.getch()
                ret = self.keypressColumns(c)
                if (ret == -1):
                    return
            except KeyboardInterrupt:
                break

    def runEdit(self):
        self.drawEditWin()
        while True:
            try:
                c = self.bodyWin.getch()
                ret = self.keypressEdit(c)
                if (ret == -1):
                    return
            except KeyboardInterrupt:
                break

    def keypressColumns(self, char):
        pageChange = 5

        if char == curses.KEY_EXIT or char == ord('q'):
            return -1

        if char == curses.KEY_DOWN:
            if self.column == 0:
                self.bodyCat.update(1)
            elif self.column == 1:
                self.bodySub.update(1)
            elif self.column == 2:
                self.bodyEnt.update(1)
            self.refreshBody()
            return

        if char == curses.KEY_UP:
            if self.column == 0:
                self.bodyCat.update(-1)
            elif self.column == 1:
                self.bodySub.update(-1)
            elif self.column == 2:
                self.bodyEnt.update(-1)
            self.refreshBody()
            return

        if char == curses.KEY_RIGHT:
            if self.column == 0:
                self.column = 1
                self.bodyCat.active = False
                self.bodySub.active = True
            elif self.column == 1:
                self.column = 2
                self.bodySub.active = False
                self.bodyEnt.active = True
            self.refreshBody()
            return

        if char == curses.KEY_LEFT:
            if self.column == 1:
                self.column = 0
                self.bodyCat.active = True
                self.bodySub.active = False
            elif self.column == 2:
                self.column = 1
                self.bodySub.active = True
                self.bodyEnt.active = False
            self.refreshBody()
            return

        if char == ord('s'):
            if self.column == 0:
                names = self.db.categoryEntries(
                        self.bodyCat.items[self.bodyCat.selected])
                self.bodyEnt.highlitedItems.update(names)
                self.refreshBody()
            if self.column == 1:
                names = self.db.categorySubcategoryEntries(
                        self.bodyCat.items[self.bodyCat.selected],
                        self.bodySub.items[self.bodySub.selected])
                self.bodyEnt.highlitedItems.update(names)
                self.refreshBody()
            if self.column == 2:
                name = self.bodyEnt.items[self.bodyEnt.selected]
                if name in self.bodyEnt.highlitedItems:
                    self.bodyEnt.highlitedItems.remove(name)
                else:
                    self.bodyEnt.highlitedItems.add(name)
                self.refreshBody()
            return

        if char == ord('d'):
            self.bodyEnt.highlitedItems.clear()
            self.refreshBody()
            return

        if char == ord(' '):
            self.modEntry()
            self.refreshBody()
            return

        if char == ord('i'):
            if not self.bodyEnt.highlitedItems:
                self.flashText("Selection is empty")
                self.refreshBody()
                return

            self.cursesExit()
            with External() as file:
                envars.setEnv(file.tempdir, self.APPDIR)
                for item in self.bodyEnt.highlitedItems:
                    stdout.write(mvars.bcolors.WARNING +
                                 "Running install script for " +
                                 item + mvars.bcolors.ENDC + '\n')
                    file.loadText(self.db.entryInfo(item)["scriptInst"])
                    file.script(self.SHELL)
                envars.unsetEnv()
            self.cursesReturn()
            self.bodyEnt.highlitedItems.clear()
            self.drawHead()

            self.refreshBody()
            return

        if char == ord('u'):
            if not self.bodyEnt.highlitedItems:
                self.flashText("Selection is empty")
                self.refreshBody()
                return

            self.cursesExit()
            with External() as file:
                envars.setEnv(file.tempdir, self.APPDIR)
                for item in self.bodyEnt.highlitedItems:
                    stdout.write(mvars.bcolors.WARNING +
                                 "Running uninstall script for " +
                                 item + mvars.bcolors.ENDC + '\n')
                    file.loadText(self.db.entryInfo(item)["scriptUinst"])
                    file.script(self.SHELL)
                envars.unsetEnv()
            self.cursesReturn()
            self.bodyEnt.highlitedItems.clear()
            self.drawHead()

            self.refreshBody()
            return

        if char == ord('n'):
            self.addEntry()
            self.refreshBody()
            return

        if char == ord('0'):
            if not self.bodyEnt.highlitedItems:
                self.flashText("Selection is empty")
                self.refreshBody()
                return

            self.rmEntry()
            self.bodyEnt.highlitedItems.clear()
            self.refreshBody()
            return

        if char == ord('#') or char == curses.KEY_RESIZE:
            self.setupAndDrawScreen()
            self.refreshBody()
            return

    def keypressEdit(self, char):
        if char == curses.KEY_EXIT or char == ord('q'):
            return -1

        if char == curses.KEY_DOWN:
            self.winEdit.update(1)
            self.drawEditWin()
            return

        if char == curses.KEY_UP:
            self.winEdit.update(-1)
            self.drawEditWin()
            return

        if char == ord(' '):
            if self.winEdit.selected == 0:
                self.winEdit.items[0] = "Name: " + self.__queryString("Name: ")
            elif self.winEdit.selected == 1:
                self.winEdit.items[1] = "Category: " +\
                        self.__queryString("Category: ")
            elif self.winEdit.selected == 2:
                self.winEdit.items[2] = "Subcategory: " +\
                        self.__queryString("Subcategory: ")
            elif self.winEdit.selected == 3:
                self.winEdit.items[3] = "Description: " +\
                        self.__queryString("Description: ")
            elif self.winEdit.selected == 4:
                script = "scriptInst"
                text = self.winEdit.items[4]
            elif self.winEdit.selected == 5:
                script = "scriptUinst"
                text = self.winEdit.items[5]
            else:
                return

            if self.winEdit.selected == 4 or self.winEdit.selected == 5:
                self.cursesExit()
                with External() as file:
                    file.loadText(text)
                    text = file.editor(self.EDITOR)

                if self.winEdit.selected == 4:
                    self.winEdit.items[4] = text
                elif self.winEdit.selected == 5:
                    self.winEdit.items[5] = text

                self.cursesReturn()
                self.drawHead()

            self.drawEditWin()
            return

        if char == ord('s'):
            if len(self.winEdit.items[0]) <= 6:
                return
            else:
                self.__applyChanges()
                return -1

        if char == ord('v'):
            if self.winEdit.selected == 4:
                script = "scriptInst"
                text = self.winEdit.items[4]
            elif self.winEdit.selected == 5:
                script = "scriptUinst"
                text = self.winEdit.items[5]
            else:
                return

            self.cursesExit()
            with External() as file:
                file.loadText(text)
                file.pager(self.PAGER)
            self.cursesReturn()
            self.drawHead()
            self.drawEditWin()

        if char == ord('#') or char == curses.KEY_RESIZE:
            self.setupAndDrawScreen()
            self.drawEditWin()
            return
