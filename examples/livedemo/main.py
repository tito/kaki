# -*- coding: utf-8 -*-

from kaki.app import App
from kivy.factory import Factory

class Live(App):
    CLASSES = {
        "UI": "live.ui"
    }
    AUTORELOADER_PATHS = [
        (".", {"recursive": True}),
    ]
    def build_app(self):
        return Factory.UI()

Live().run()
