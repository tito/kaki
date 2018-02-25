# -*- coding: utf-8 -*-
"""
Kaki Application
================

"""

import os
import sys
import traceback
from os.path import join, realpath
from kivy.app import App as BaseApp
from kivy.logger import Logger
from kivy.clock import Clock, mainthread
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.base import ExceptionHandler, ExceptionManager
try:
    from monotonic import monotonic
except ImportError:
    monotonic = None
try:
    from importlib import reload
    PY3 = True
except ImportError:
    PY3 = False


class E(ExceptionHandler):
    def handle_exception(self, inst):
        App.get_running_app().set_error(inst, tb=traceback.format_exc())
        return ExceptionManager.PASS


ExceptionManager.add_handler(E())


class App(BaseApp):
    """Kaki Application class
    """

    #: Control either we activate debugging in the app or not
    #: Defaults depend if "DEBUG" exists in os.environ
    DEBUG = "DEBUG" in os.environ

    #: If true, it will require the foreground lock on windows
    FOREGROUND_LOCK = False

    #: List of KV files under management for auto reloader
    KV_FILES = []

    #: List of path to watch for autoreloading
    AUTORELOADER_PATHS = []

    #: List of extensions to ignore
    AUTORELOADER_IGNORE_EXTS = ["*.pyc"]

    __events__ = ["on_idle", "on_wakeup"]

    def build(self):
        if self.DEBUG:
            Logger.info("{}: Debug mode activated".format(self.appname))
            self.enable_autoreload()
            self.patch_builder()
            self.bind_key(286, self.rebuild)
        if self.FOREGROUND_LOCK:
            self.prepare_foreground_lock()

        self.state = None
        self.approot = None
        self.root = self.get_root()
        self.rebuild(first=True)

        return super(App, self).build()

    def get_root(self):
        """
        Return a root widget, that will contains your application.
        It should not be your application widget itself, as it may
        be destroyed and recreated from scratch when reloading.

        By default, it returns a RelativeLayout, but it could be
        a Viewport.
        """
        return Factory.RelativeLayout()

    def build_app(self, first=False):
        """Must return your application widget.

        If `first` is set, it means that will be your first time ever
        that the application is built. Act according to it.
        """
        raise NotImplemented()

    def unload_app_dependencies(self):
        """
        Called when all the application dependencies must be unloaded.
        Usually happen before a reload
        """
        for path in self.KV_FILES:
            Builder.unload_file(path)
        for name, module in self.CLASSES.items():
            Factory.unregister(name)

    def load_app_dependencies(self):
        """
        Load all the application dependencies.
        This is called before rebuild.
        """
        for path in self.KV_FILES:
            Builder.load_file(path)
        for name, module in self.CLASSES.items():
            Factory.register(name, module=module)

    def rebuild(self, *largs, **kwargs):
        Logger.debug("{}: Rebuild the application".format(self.appname))
        first = kwargs.get("first", False)
        try:
            if not first:
                self.unload_app_dependencies()
            self.load_app_dependencies()
            self.set_widget(None)
            self.approot = self.build_app()
            self.set_widget(self.approot)
            self.apply_state(self.state)
        except Exception as e:
            import traceback
            Logger.exception("{}: Error when building app".format(self.appname))
            self.set_error(repr(e), traceback.format_exc())

    @mainthread
    def set_error(self, exc, tb=None):
        from kivy.core.window import Window
        lbl = Factory.Label(
            text_size=(Window.width - 100, None),
            text="{}\n\n{}".format(exc, tb or ""))
        self.set_widget(lbl)

    def bind_key(self, key, callback):
        """
        Bind a key (keycode) to a callback
        (cannot be unbind)
        """
        from kivy.core.window import Window

        def _on_keyboard(window, keycode, *largs):
            if key == keycode:
                return callback()

        Window.bind(on_keyboard=_on_keyboard)

    @property
    def appname(self):
        """
        Return the name of the application class
        """
        return self.__class__.__name__

    def enable_autoreload(self):
        """
        Enable autoreload manually. It is activated automatically
        if "DEBUG" exists in environ.

        It requires the `watchdog` module.
        """
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler
        except ImportError:
            Logger.warn("{}: Autoreloader is missing watchdog".format(
                self.appname))
            return
        Logger.info("{}: Autoreloader activated".format(self.appname))
        rootpath = self.get_root_path()
        self.w_handler = handler = FileSystemEventHandler()
        handler.dispatch = self._reload_from_watchdog
        self._observer = observer = Observer()
        for path in self.AUTORELOADER_PATHS:
            observer.schedule(
                handler, join(rootpath, path),
                recursive=True)
        observer.start()

    def _reload_from_watchdog(self, event):
        from watchdog.events import FileModifiedEvent
        if not isinstance(event, FileModifiedEvent):
            return
        if event.src_path.endswith(".pyc"):
            return

        if event.src_path.endswith(".py"):
            # source changed, reload it
            try:
                Builder.unload_file(event.src_path)
                self._reload_py(event.src_path)
            except Exception as e:
                import traceback
                self.set_error(repr(e), traceback.format_exc())
                return

        Clock.unschedule(self.rebuild)
        Clock.schedule_once(self.rebuild, 0.1)

    def _reload_py(self, filename):
        # we don't have dependency graph yet, so if the module actually exists
        # reload it.
        orig_filename = filename
        rootpath = self.get_root_path()
        if filename.startswith(rootpath):
            filename = filename[len(rootpath):]
        if filename.startswith("/"):
            filename = filename[1:]
        module = filename[:-3].replace("/", ".")
        Logger.debug("{}: Translated {} to {}".format(
            self.appname, orig_filename, module))
        if module in sys.modules:
            Logger.debug("{}: Module exist, reload it".format(self.appname))
            reload(sys.modules[module])

    def prepare_foreground_lock(self):
        """
        Try forcing app to front permanently to avoid windows
        pop ups and notifications etc.app

        Requires fake fullscreen and borderless.

        .. note::

            This function is called automatically if `FOREGROUND_LOCK` is set

        """
        try:
            import ctypes
            LSFW_LOCK = 1
            ctypes.windll.user32.LockSetForegroundWindow(LSFW_LOCK)
            Logger.info("App: Foreground lock activated")
        except Exception:
            Logger.warn("App: No foreground lock available")

    def set_widget(self, wid):
        """
        Clear the root container, and set the new approot widget to `wid`
        """
        self.root.clear_widgets()
        self.approot = wid
        if wid is None:
            return
        self.root.add_widget(self.approot)
        try:
            wid.do_layout()
        except Exception:
            pass

    def get_root_path(self):
        """
        Return the root file path
        """
        return realpath(os.getcwd())

    # State management
    def apply_state(self, state):
        """Whatever the current state is, reapply the current state
        """
        pass

    # Idle management leave
    def install_idle(self, timeout=60):
        """
        Install the idle detector. Default timeout is 60s.
        Once installed, it will check every second if the idle timer
        expired. The timer can be rearm using :func:`rearm_idle`.
        """
        if monotonic is None:
            Logger.exception(
                "{}: Cannot use idle detector, monotonic is missing".format(
                    self.appname))
        self.idle_timer = None
        self.idle_timeout = timeout
        Clock.schedule_interval(self._check_idle, 1)
        self.root.bind(
            on_touch_down=self.rearm_idle,
            on_touch_up=self.rearm_idle)

    def _check_idle(self, *largs):
        if not hasattr(self, "idle_timer"):
            return
        if self.idle_timer is None:
            return
        if monotonic() - self.idle_timer > self.idle_timeout:
            self.idle_timer = None
            self.dispatch("on_idle")

    def rearm_idle(self, *largs):
        """
        Rearm the idle timer
        """
        if not hasattr(self, "idle_timer"):
            return
        if self.idle_timer is None:
            self.dispatch("on_wakeup")
        self.idle_timer = monotonic()

    def on_idle(self, *largs):
        """
        Event fired when the application enter the idle mode
        """
        pass

    def on_wakeup(self, *largs):
        """
        Event fired when the application leaves idle mode
        """
        pass

    # internals
    def patch_builder(self):
        Builder.orig_load_string = Builder.load_string
        Builder.load_string = self._builder_load_string

    def _builder_load_string(self, string, **kwargs):
        from inspect import getframeinfo, stack
        caller = getframeinfo(stack()[1][0])
        kwargs["filename"] = caller.filename
        return Builder.orig_load_string(string, **kwargs)
