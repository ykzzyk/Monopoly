from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
import webbrowser

import GUI.HomeScreen


class Feedback(GridLayout, Screen):

    def __init__(self, **kwargs):
        super(Feedback, self).__init__(**kwargs)

        self.app = App.get_running_app()

        self.rows = 3
        self.padding = [self.app.width/7.2, 0, self.app.width/7.2, 0]

        self.add_widget(Label(text='[b][color=#FF7F00]Help & Feedback[/color][/b]', font_size=self.app.width/28.8, color=[1, 1, 1, 1],
                              markup=True, size_hint_y=0.5))

        # Middle Design

        self.add_widget(
            Button(text='[b][color=#FFB533]TEXT[/color][/b]', font_size=self.app.width/57.6, color=[1, 1, 1, 1],
                  markup=True, size_hint_y=3.5))


        # Buttom Design
        self.buttom = GridLayout(cols=2)

        self.buttom.padding = [self.app.width/7.2, self.app.width/28.8, self.app.width/7.2, self.app.width/19.2]
        self.buttom.spacing = [self.app.width/8.5, 0]

        self.button_back = Button(text='[b]Back[/b]', font_size=self.app.width/57.6, markup=True, on_press=self.home_screen_page)
        self.buttom.add_widget(self.button_back)

        self.button_contact = Button(text='[b]Contact Us[/b]', font_size=self.app.width/57.6, markup=True, on_press=self.open_browser)
        self.buttom.add_widget(self.button_contact)

        self.add_widget(self.buttom)

    def home_screen_page(self, event):
        self.app.screen_manager.switch_to(GUI.HomeScreen.HomeScreen(name='home_screen'))

    def open_browser(self, event):
        webbrowser.open("mailto:yzhang5@mail.stmarytx.edu", new=1)
