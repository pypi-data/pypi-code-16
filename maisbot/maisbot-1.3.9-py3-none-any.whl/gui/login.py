from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput


class LoginScreen(GridLayout):

    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        self.cols = 2
        self.add_widget(Label(text='Email'))
        self.email = TextInput(multiline=False)
        self.add_widget(self.email)
        self.add_widget(Label(text='Senha'))
        self.password = TextInput(password=True, multiline=False)
        self.add_widget(self.password)
