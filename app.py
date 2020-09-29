from kivy.app import App
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition

import GUI.HomeScreen
import GUI.GameLobby
import GUI.GameBoard
import GUI.Feedback

import Util.util


class MonopolyApp(App):

    def build(self):
        Window.fullscreen = 'auto'
        self.title = 'Monopoly - The Computer Science Edition'
        self.width = Window.width
        self.height = Window.height

        self.screen_manager = ScreenManager(transition=NoTransition())
        self.screen_manager.add_widget(GUI.HomeScreen.HomeScreen(name='home_screen'))
        self.screen_manager.add_widget(GUI.GameLobby.GameLobby(name='game_lobby'))
        self.screen_manager.add_widget(GUI.Feedback.Feedback(name='feedback'))

        return self.screen_manager


if __name__ == '__main__':

    MonopolyApp().run()
