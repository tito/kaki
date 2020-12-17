"""
This is an example using Kaki with Kivy modules.
"""

import os


from kaki.app import App
from kivy.factory import Factory




# main app class for kaki app with kivy style
class Main(App):

    # root app name/title
    name = "Kaki App Example"

    # version number
    vernum = "0.1.4"

    # window title
    title = "%s v%s" % (name, vernum)

    # by default it will return to False
    # set this to True so you can make a change to your .kv file
    DEBUG = True

    # *.kv files to watch
    KV_FILES = {
        # screen manager
        os.path.join(os.getcwd(), "kv_style/manager_screens.kv"),

        # screen one
        os.path.join(os.getcwd(), "kv_style/screens/screen_one.kv")
    }

    # class to watch
    CLASSES = {
        # screen manager
        "ManagerScreens": "kv_style.manager_screens", # look at the line 57

        # screen one
        "ScreenOne": "kv_style.screens.screen_one"

    }

    # auto reload path
    AUTORELOADER_PATHS = [
        (".", {"recursive": True}),
    ]


    # build app
    def build_app(self):
        FMS = self.fms = Factory.ManagerScreens() # look at the line 42

        return FMS




# launch the app
if __name__ == "__main__":
    Main().run()