from kivy.app import App
from kivy.uix.label import Label
import GUI.HomeScreen
import Util.util
from kivy.core.window import Window


class MonopolyApp(App):

    def build(self):
        Window.fullscreen = 'auto'
        self.title = 'Monopoly - The Computer Science Edition'
        return GUI.HomeScreen.HomeScreen()


if __name__ == '__main__':
    MonopolyApp().run()
