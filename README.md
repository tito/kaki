# Kaki - Advanced application library for Kivy

This library enhance Kivy frameworks with opiniated features such as:

- Auto reloading kv or py (`watchdog` required, limited to some uses cases)
- Idle detection support
- Foreground lock (windows only)

<br>

## Installation

Using pip
```txt
pip install kaki
```

<a href="https://pypi.org/project/kaki/">pypi link</a>

<br>

## Example

*__examples/livedemo/main.py__*

This is a bootstrap that will:
- automatically declare the module `live.ui` (`live/ui.py`) as a provider for the widget `UI`
- build the application widget, and show it to a window

If the bootstrap is started with the environment variable `DEBUG=1`, it will start a watchdog, and listen for changes, according to `AUTORELOADER_PATHS`.
When something changes, the current application widget will be cleared out, and a new one will be instanciated, after reloading.

```python
from kaki.app import App
from kivy.factory import Factory

class Live(App):
    CLASSES = {
        "UI": "live.ui"     # <----------#|
    }                                    #|
    AUTORELOADER_PATHS = [               #|     This classes will be call as highest root class.
        (".", {"recursive": True}),      #|---- If you make two screens and saved your *.kv files
    ]                                    #|     yout main window will return to the first screen.
    def build_app(self):                 #|
        return Factory.UI() # <----------#|

Live().run()
```

<br>


## Application class configuration


    #: Control either we activate debugging in the app or not
    #: Defaults depend if "DEBUG" exists in os.environ
    DEBUG = "DEBUG" in os.environ

    #: If true, it will require the foreground lock on windows
    FOREGROUND_LOCK = False

    #: List of KV files under management for auto reloader
    KV_FILES = []

    #: List of path to watch for autoreloading
    AUTORELOADER_PATHS = [
        # (".", {"recursive": False}),
    ]

    #: List of extensions to ignore
    AUTORELOADER_IGNORE_PATTERNS = [
        "*.pyc", "*__pycache__*"]

    #: Factory classes managed by kaki
    CLASSES = {}

    #: Idle detection (if True, event on_idle/on_wakeup will be fired)
    #: Rearming idle can also be done with rearm_idle()
    IDLE_DETECTION = False

    #: Default idle timeout
    IDLE_TIMEOUT = 60

    #: Raise error
    #: When the DEBUG is activated, it will raise any error instead
    #: of showing it on the screen. If you still want to show the error
    #: when not in DEBUG, put this to False
    RAISE_ERROR = True

<br>


## Idle Management

If configuration `IDLE_DETECTION` is `True`, then it will automatically listen for touch down/move.
When no event happen, after `IDLE_TIMEOUT` seconds, it will trigger the `on_idle` event on the application class.
As soon as a touch event occurs, `on_wakeup` event will be triggered on the application class.

If you are playing video on want to not trigger the idle detection, use `rearm_idle` on the application class to rearm the detection from 0
seconds.

<br>

## Cases

Each person who develope with __Kivy framework__, __KivyMD__ and __Kaki__ has their own implementation.
From method to approach, folders stucture, *operating system* environment and many more.

There's two example in *__examples__* folder.

<br>

__Kaki Using Kivy Module:__

- Where to look:
    ```text
    examples/menudemo/kvstyle.py
    ```
- preview:
![image kvstyle](/examples/documentation/Kaki_Using_Kivy_Modules.png)

<br>

__Kaki Using Kivy or KivyMD Module or Both:__

- Where to look:
    ```text
    examples/menudemo/mdstyle.py
    ```
- preview:
![image mdstyle](/examples/documentation/Kaki_Using_Kivy_and_KivyMD_Modules.png)

<br>

__NOTE:__

If you want to access and run it from your Code Editor or IDE. You need to open it from that directory.
Otherwise it will be look like this:
![image error](/examples/documentation/Kaki_Error_Example.png)

<br>

___

###### end of readme.