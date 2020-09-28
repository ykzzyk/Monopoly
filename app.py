from kivy.app import App
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen

import GUI.HomeScreen
import GUI.GameLobby
import GUI.GameBoard

import Util.util


class MonopolyApp(App):

    def build(self):
        Window.fullscreen = 'auto'
        self.title = 'Monopoly - The Computer Science Edition'
        self.width = Window.width
        self.height = Window.height

        self.screen_manager = ScreenManager()
        self.screen_manager.add_widget(GUI.HomeScreen.HomeScreen(name='home_screen'))
        self.screen_manager.add_widget(GUI.GameLobby.GameLobby(name='game_lobby'))
        self.screen_manager.add_widget(GUI.GameBoard.GameBoard(name='game_board'))

        # screens = [Screen(name='home_screen'), Screen(name='game_lobby'), Screen(name='game_board')]
        #
        # screen_manager.switch_to(screens[0])
        # screen_manager.switch_to(screens[1], direction='right')

        return self.screen_manager


if __name__ == '__main__':

    MonopolyApp().run()
