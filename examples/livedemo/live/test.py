# -*- coding: utf-8 -*-

from kivy.factory import Factory as F
from kivy.lang import Builder

Builder.load_string("""
#:import rgba kivy.utils.get_color_from_hex
<UIUserLabel@Label>:
    index: 0
    canvas.before:
        Color:
            rgba: rgba("#ff000044") if root.index % 2 else rgba("#00ff0044")
        Rectangle:
            pos: self.pos
            size: self.size

<UISection@Label>:
    text: "NOP"
    text_size: self.width - dp(48), None
    bold: True

<UI>:
    cols: 1
    Button:
        text: "hello world"
        on_release: root.callback()
        size_hint_y: None
        height: dp(48)
    RecycleView:
        id: rv
        key_viewclass: "viewclass"
        RecycleGridLayout:
            cols: 1
            size_hint_y: None
            height: self.minimum_height
            default_size_hint: 1, None
            default_size: None, dp(48)
""")

class UI(F.GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.callback()

    def callback(self):
        data = [
            {
                "text": "User {}".format(i),
                "index": i,
                "viewclass": "UIUserLabel"
            }
            for i in range(500)
        ]
        data[10] = {
            "viewclass": "UISection"
        }
        self.ids.rv.data = data
