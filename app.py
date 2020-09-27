from kivy.app import App
from kivy.uix.label import Label
import GUI.HomeScreen
import Util.util
from kivy.core.window import Window


class MonopolyApp(App):

    def build(self):
        self.title = 'Monopoly - The Computer Science Edition'
        Window.fullscreen = 'auto'
        return GUI.HomeScreen.HomeScreen()


if __name__ == '__main__':
    MonopolyApp().run()
