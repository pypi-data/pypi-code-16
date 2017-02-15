import os
import glob
import sys

import functools
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import unquote

from tkinter import Tk, filedialog

try:
    from .patch import update_probesysfs
    update_probesysfs()
except ImportError:
    pass

import kivy

kivy.require('1.9.1')

kivy.Config.set('kivy', 'desktop', 1)
kivy.Config.set('input', 'mouse', 'mouse,disable_multitouch')
kivy.Config.set('graphics', 'width', '420')
kivy.Config.set('graphics', 'height', '420')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty


import slashlock

try:
    _BASE_DIR = sys._MEIPASS  # Used by PyInstaller for onefile binaries
except:
    _BASE_DIR = os.path.dirname(os.path.abspath(__file__))

_KV_DIR = os.path.join(_BASE_DIR, 'kvs')  # Directory containing kv files
_EXECUTOR = ThreadPoolExecutor(max_workers=1)

for kv in glob.glob(os.path.join(_KV_DIR, "*.kv")):
    Builder.load_file(kv)


_BLUE_BLACK = (133/255, 133/255, 232/255, 1)  # Also defined in styles.kv


class BlueBlackButton(Button):

    def on_disabled(self, obj, disabled):
        if disabled:
            self.background_color = (133/255, 133/255, 232/255, 0.2)
        else:
            self.background_color = _BLUE_BLACK


class ChooseDirectoryScreen(Screen):

    def _directory_selected(self, btn, future):
        btn.disabled = False
        save_dir = App.get_running_app().save_directory
        label = self.ids['save_directory_label']
        label.text = save_dir
        label.parent.dispatch_generic('on_size')

    def click_continue(self):
        sm = App.get_running_app().root.ids['screen_manager']
        sm.current = "file_name_screen"

    def _choose_directory(self):
        Tk().withdraw()  # Don't show the tk window
        # Set the current directory to where the file is located
        App.get_running_app().save_directory = filedialog.askdirectory(
            initialdir=os.path.dirname(App.get_running_app().filepath)
        )

    def choose_directory(self, btn=None):
        btn.disabled = True

        future_result = _EXECUTOR.submit(self._choose_directory)
        future_result.add_done_callback(
            functools.partial(self._directory_selected, btn)
        )


class AppContainer(BoxLayout):
    pass


class CryptoApp(App):

    file_status = 'unlocked'
    filename = StringProperty('')
    save_directory = StringProperty('')
    save_as = StringProperty('')
    lock_or_unlock = StringProperty('Lock')
    processing_status = StringProperty('')
    result_message = StringProperty('')
    _passphrase = StringProperty('')
    _metadata = None

    @property
    def _screen_manager(self):
        return self.root.ids['screen_manager']

    def build(self):
        return AppContainer()

    def _validate_passphrase(self):
        self._passphrase = self.root.ids[
            'set_passphrase_screen'].ids['passphrase'].text
        confirm_passphrase = self.root.ids[
            'set_passphrase_screen'].ids['confirm_passphrase'].text

        continue_button = self.root.ids['set_passphrase_screen'].ids['password_continue_button']  # NOQA

        if all([self._passphrase, confirm_passphrase]) and self._passphrase == confirm_passphrase:
            continue_button.disabled = False
        else:
            continue_button.disabled = True

    def on_drop(self, *args):
        # Remove quotes that were inserted to replace spaces and hyphens
        sm = self._screen_manager
        if sm.current == 'drop_screen':

            self.filepath = unquote(args[1].decode('utf-8'))
            self.filename = os.path.basename(self.filepath)
            self.save_directory = os.path.dirname(self.filepath)

            self._metadata = slashlock._metadata_from_locked_file(
                self.filepath, self._passphrase)

            if self._metadata:
                self.file_status = 'locked'
                self.lock_or_unlock = 'Unlock'
                self.save_as = self._metadata.name.decode('utf-8')
            else:
                self.save_as = '.'.join([self.filename, 'locked'])

            sm = self.root.ids['screen_manager']
            sm.current = "choose_directory_screen"

    def randomize_name(self):
        """ Randomize the filename """
        self.save_as = slashlock.randomize_name()

    def run_lock_or_unlock(self):
        """ Call the correct method """

        self.processing_status = " ".join([
            "Saving",
            self.filename,
            'as',
            os.path.join(self.save_directory, self.save_as)])

        if self.file_status == 'unlocked':
            self._encrypt()
        else:
            self._decrypt()

        sm = self.root.ids['screen_manager']
        sm.current = "processing_screen"

    def _processing_complete(self, result):
        """ Go to the processing complete screen """

        self.result_message = 'Successfully saved {} as {}'.format(
            self.filename,
            os.path.join(self.save_directory, self.save_as),
        )

        self._screen_manager.current = 'result_screen'

    def _encrypt(self):
        """ Encrypt the file """

        future_result = _EXECUTOR.submit(functools.partial(
            slashlock.lock,
            self.filepath,
            self._passphrase,
            save_dir=self.save_directory,
            save_as=self.save_as,
        ))

        future_result.add_done_callback(self._processing_complete)

    def _decrypt(self):
        """ Encrypt the file """

        future_result = _EXECUTOR.submit(functools.partial(
            slashlock.unlock,
            self.filepath,
            self._passphrase,
            save_dir=self.save_directory,
            save_as=self.save_as,
        ))
        future_result.add_done_callback(self._processing_complete)

    def _reset(self, passphrase=False):
        """ Reset the application variables """

        self.file_status = 'unlocked'
        self.filename = ''
        self.save_directory = ''
        self.save_as = ''
        self.lock_or_unlock = 'Lock'
        self.processing_status = ''
        self._metadata = None
        self.result_message = ''

        if passphrase:
            self._passphrase = ''
        else:
            self._screen_manager.current = 'drop_screen'

    def set_passphrase(self):
        """ Set the passphrase """

        continue_button = self.root.ids['set_passphrase_screen'].ids['password_continue_button']  # NOQA

        if continue_button.disabled:
            return

        self._passphrase = self.root.ids[
            'set_passphrase_screen'].ids['passphrase'].text

        sm = self.root.ids['screen_manager']
        sm.current = "drop_screen"


def main():
    app = CryptoApp()
    app.title = 'Slashlock'
    Window.bind(on_dropfile=app.on_drop)
    app.run()

if __name__ == "__main__":
    main()
