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
from kivy.properties import NumericProperty
import webbrowser

# Imports tools
import tools

# Importing all GUI
import gui

cwd = pathlib.Path(os.path.abspath(__file__)).parent
gui_widgets = cwd / 'gui'

tools.fh.import_dir(gui_widgets)


class Start(Screen):
    pass


class Feedback(Screen):
    def send_email(self, event):
        webbrowser.open("mailto:yzhang5@mail.stmarytx.edu", new=1)
        print('open email successfully!')


class Home(Screen):
    pass


class WindowManager(ScreenManager):
    pass


class MonopolyApp(App):

    def build(self):
        Window.fullscreen = 0
        Window.clearcolor = (1, 1, 1, 1)
        self.title = 'Monopoly'

        return kv


if __name__ == "__main__":
    # Loading the primary application .kv file
    kv = Builder.load_file("kivy.kv")
    MonopolyApp().run()
