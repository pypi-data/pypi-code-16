#!/usr/bin/env python3


import argparse
import os
from mimetypes import guess_type
import curses
import curses.textpad
import shutil

import requests


default_format = ('Season {season}/{episode:02d} - '
                  '{title}{ext}')


class Interface:
    """Interface
    An interface class to handle the curses UI stuff.
    """

    def __init__(self, files, episodes, root_dir, show_name):
        """__init__
        params:
            files: list: A list of files before you modify them.
            episodes: list: A list of the API results for the show.
            root_dir: str: The root directory of the show folder.
            show_name: str: The name of the show.
        """
        self.files = files
        self.episodes = episodes
        self.root_dir = root_dir
        self.show_name = show_name

    def __enter__(self):
        self.screen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        self.screen.keypad(True)
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(2, curses.COLOR_YELLOW, -1)
        return self

    def __exit__(self, *_):
        curses.echo()
        curses.nocbreak()
        self.screen.keypad(False)
        curses.endwin()
        return None

    def main(self): 
        """main
        Handle the main interface and key input.
        """
        self.chosen_format = default_format
        index = 0
        offset = 0
        key = 0
        items = list(zip(self.files, self.episodes))
        selected = [False for x in items]
        while True:
            height, width = self.screen.getmaxyx()
            self.screen.clear()
            self.screen.addstr(0, 0, '{}:'.format(self.show_name.title()),
                               curses.A_BOLD)
            self.draw_itemlist(items, index, offset, selected)
            #self.screen.addstr(0, 0, str(key))
            self.screen.refresh()
            key = self.screen.getch()
            if index+offset > len(items):
                index -= 1

            # Handle keypress
            if key == 113:
                break

            if key == 99:
                win = curses.newwin(1, width, height-1, 0)
                textbox = curses.textpad.Textbox(win)
                new_format = textbox.edit()
                if new_format.strip() != '':
                    self.chosen_format = new_format
                continue

            if key == 10:
                self.__exit__()
                move_files(items, self.root_dir)
                return None

            if key == 114:
                for item_index, item in enumerate(selected):
                    if item:
                        del items[item_index]
                selected = [False for x in items]
                    
            if key == 32:
                selected[offset+index] = not selected[offset+index]

            if key == 410:
                height, width = self.screen.getmaxyx()
                while index > height-4:
                    index -= 1
                    offset += 1
                while offset > len(items)-1:
                    offset -= 1

            if key == 338:
                # Move selection down
                for selindex, active in reversed(list(enumerate(selected))):
                    if not active:
                        continue
                    offindex = selindex
                    if offindex == len(items)-1:
                        index = len(items)-1-offset
                        break
                    one = items[offindex]
                    two = items[offindex+1]
                    items[offindex], items[offindex+1] = ((two[0], one[1]),
                                                          (one[0], two[1]))
                    selected[offindex] = False
                    selected[offindex+1] = True

            if key == 339:
                # Move selection up
                for selindex, active in enumerate(selected):
                    if not active:
                        continue
                    offindex = selindex
                    if offindex == 0:
                        break
                    one = items[offindex]
                    two = items[offindex-1]
                    items[offindex], items[offindex-1] = ((two[0], one[1]),
                                                          (one[0], two[1]))
                    selected[offindex] = False
                    selected[offindex-1] = True

            if key == 258 or key == 338 or key == 32:
                # Move down
                #if index+offset == len(items)-1:
                #    continue
                index += 1
                while index > height-5:
                    index -= 1
                    offset += 1
                #while offset > :
                #    offset -= 1

            if key == 259 or key == 339:
                # Move up
                index -= 1
                while index < 0:
                    index = 0
                    offset -= 1
                while offset < 0:
                    offset = 0
        return None

    def draw_itemlist(self, items, index, offset, selected):
        """draw_itemlist
        Display a list of items in the curses UI.

        params:
            items: list: A list of items to display.
            index: int: The current index of your cursor on screen.
            offset: int: The offset to start displaying items at.
            selected: list: A list of selected items.
        """
        height, width = self.screen.getmaxyx()
        for yindex, item in enumerate(items[offset:]):
            name, episode = item
            name, __ = name
            if yindex == height-4:
                break
            options = 0
            if yindex == index:
                _, ext = os.path.splitext(name)
                season_episode = self.chosen_format.format(
                                 episode=episode['number'],
                                 season=episode['season'],
                                 title=episode['name'],
                                 ext=ext,
                                 index=offset+yindex)
                self.screen.addstr(height-1, 0, '[C]hange: ')
                self.screen.addstr(height-1, 10, season_episode[:width-12],
                                   curses.A_DIM)
                options |= curses.A_BOLD

            if selected[yindex+offset]:
                options |= curses.A_REVERSE

            epname = episode['name']
            self.screen.addstr(2+yindex, 0, name[:int(width//2)-2], options)
            self.screen.addstr(2+yindex, int(width//2)+2,
                               epname[:int(width//2)-2],
                               options | curses.color_pair(2))
        return None


def move_files(items, root_dir, chosen_format=default_format):
    """move_files
    Moves the files from the old format to the new format.

    params:
        items: list: A zipped list of both the old and new files.
        root_dir: str: The root dir of the show folder.
        chosen_format: str: The new chosen format.
    """
    for index, (fdata, new_data) in enumerate(items):
        fname, fpath = fdata
        _, ext = os.path.splitext(fname)
        season = new_data['season']
        episode = new_data['number']
        episode_name = new_data['name']
        new_dir = os.path.join(root_dir, chosen_format.format(
                  season=season,
                  episode=episode,
                  title=episode_name,
                  ext=ext,
                  index=index))
        new_folder = '/'.join(new_dir.split('/')[:-1])
        if not os.path.isdir(new_folder):
            os.makedirs(new_folder)
        if not os.path.exists(new_dir):
            shutil.move(fpath, new_dir)
            #shutil.copy(fpath, new_dir)
    return None 


def sorted_walk(root_dir):
    """sorted_walk
    A generator that walks through each subdir in a .lower() sorted fashion.

    params:
        root_dir: str: The root directory to start walking from.
    """
    files = sorted(os.listdir(root_dir), key=lambda x: x.lower())
    for index, name in enumerate(files):
        fullpath = os.path.join(root_dir, name)
        if os.path.isdir(fullpath):
            yield from sorted_walk(fullpath)
        else:
            yield name, fullpath
    raise StopIteration


def default_input(prompt, default=None):
    """default_input
    Like input, but with a default param.

    params:
        prompt: str: The prompt for the input.
        default: The default value if no input is entered.
    """
    result = input(prompt)
    if result.strip() == '':
        return default
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('directory')
    args = parser.parse_args()
    show_directory = args.directory

    if not os.path.exists(show_directory):
        print('Could not find that directory.')
        return None

    files = []
    for filename, filepath in sorted_walk(show_directory):
        mtype = guess_type(filename)[0]
        if mtype is None or not mtype.startswith('video'):
            continue
        files.append((filename, filepath))

    default_name = [x for x in show_directory.split('/') if x != ''][-1]
    name_format = 'Show name [{}]: '.format(default_name)
    show_name = default_input(name_format, default_name)
    req = requests.get('http://api.tvmaze.com/search/shows?q={}'.format(show_name))
    shows = req.json()
    print( '[0] Exit' )

    for index, data in enumerate(shows):
        info = data['show']
        _type = info['type']
        genre = ', '.join(info['genres'])
        name = info['name']
        print( '[{}] - {} / {} - {}'.format(index+1, name, _type, genre) )

    number = int(default_input('Please enter a number [1]: ', 1))
    if number < 1 or number > len(shows):
        return None
    
    url = shows[number-1]['show']['_links']['self']['href'] + '/episodes'
    req = requests.get(url)
    episodes = req.json()

    with Interface(files, episodes, show_directory, show_name) as ui:
        ui.main()
    return None


if __name__ == "__main__":
    main()
