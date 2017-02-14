import kivy
from kivy.app import App
from gui.login import LoginScreen

kivy.require('1.9.1')


class KivyApp(App):

    def build(self):
        return LoginScreen()


def start():
    app = KivyApp()
    app.run()


if __name__ == '__main__':
    start()
