from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.graphics import Rectangle, Color
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
import webbrowser


class Logo(Screen):
    pass


class Feedback(Screen):
    def send_email(self, event):
        webbrowser.open("mailto:yzhang5@mail.stmarytx.edu", new=1)
        print('open email successfully!')


class Home(Screen):
    pass


class Lobby(Screen):
    pass


class Game(Screen):
    pass


class WindowManager(ScreenManager):
    pass


kv = Builder.load_file("kivy.kv")


class MonopolyApp(App):

    def build(self):
        Window.fullscreen = 'auto'
        Window.clearcolor = (1, 1, 1, 1)
        self.title = 'Monopoly - The Computer Science Edition'

        return kv


if __name__ == "__main__":
    MonopolyApp().run()
