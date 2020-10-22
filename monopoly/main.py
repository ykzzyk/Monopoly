import os
import sys
import pathlib

from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.graphics import Rectangle, Color
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.graphics import *
import webbrowser

# Imports tools
import tools

# Importing all GUI
cwd = pathlib.Path(os.path.abspath(__file__)).parent
gui_widgets = cwd / 'gui'

tools.fh.import_dir(gui_widgets)


class Logo(Screen):
    pass


class Feedback(Screen):
    def send_email(self, event):
        webbrowser.open("mailto:yzhang5@mail.stmarytx.edu", new=1)
        print('open email successfully!')


class Home(Screen):
    pass


class Lobby(Screen):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.random_text = "1111"

    def change_text(self):
        self.random_text = "asdf"


class Game(Screen):
    pass


class WindowManager(ScreenManager):
    pass


class MonopolyApp(App):

    def build(self):
        Window.fullscreen = 'auto'
        Window.clearcolor = (1, 1, 1, 1)
        self.title = 'Monopoly - The Computer Science Edition'

        return kv


if __name__ == "__main__":
    # Loading the primary application .kv file
    kv = Builder.load_file("kivy.kv")
    MonopolyApp().run()
