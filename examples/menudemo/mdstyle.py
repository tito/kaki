"""
This is an example using Kaki with Kivy modules or KidyMD modules.
"""

import os


from kaki.app import App as MainApp
from kivy.factory import Factory
from kivymd.app import MDApp as SecondApp




# main app class for kaki app with kivymd style
class Main(MainApp, SecondApp):
    """ You can use two widgets class from kivy and kivymd """

    # root app name/title
    name = "Kaki App Example ft. MD"

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
        os.path.join(os.getcwd(), "md_style/manager_screens.kv"),

        # screen one
        os.path.join(os.getcwd(), "md_style/screens/screen_one.kv")
    }

    # class to watch
    CLASSES = {
        # screen manager
        "ManagerScreens": "md_style.manager_screens", # look at the line 59

        # screen one
        "ScreenOne": "md_style.screens.screen_one"

    }

    # auto reload path
    AUTORELOADER_PATHS = [
        (".", {"recursive": True}),
    ]


    # build app
    def build_app(self):
        FMS = self.fms = Factory.ManagerScreens() # look at the line 59

        self.theme_cls.theme_style = "Dark"

        return FMS




# launch the app
if __name__ == "__main__":
    Main().run()