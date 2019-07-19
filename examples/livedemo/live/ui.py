# -*- coding: utf-8 -*-

from kivy.factory import Factory as F
from kivy.lang import Builder

Builder.load_string("""
<UI>:
    cols: 1
    Label:
        text: str(slider.value)
    Slider:
        id: slider
""")

class UI(F.GridLayout):
    pass
