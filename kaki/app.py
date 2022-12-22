# -*- coding: utf-8 -*-
"""
Kaki Application
================

"""

import sys
original_argv = sys.argv

import os
import sys
import traceback
from os.path import join, realpath
from fnmatch import fnmatch
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
        if isinstance(inst, (KeyboardInterrupt, SystemExit)):
            return ExceptionManager.RAISE
        app = App.get_running_app()
        if not app.DEBUG and not app.RAISE_ERROR:
            return ExceptionManager.RAISE
        app.set_error(inst, tb=traceback.format_exc())
        traceback.print_exc()
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

    #: Auto install idle detection check when activated
    IDLE_DETECTION_AUTO_START = True

    #: Default idle timeout
    IDLE_TIMEOUT = 60

    #: Raise error
    #: When the DEBUG is activated, it will raise any error instead
    #: of showing it on the screen. If you still want to show the error
    #: when not in DEBUG, put this to False
    RAISE_ERROR = True

    __events__ = ["on_idle", "on_wakeup"]

    def build(self):
        Logger.info("Kaki: Application controlled by Kaki")
        if self.DEBUG:
            Logger.info("Kaki: Debug mode activated")
            self.enable_autoreload()
            self.patch_builder()
            self.bind_key(286, self.rebuild)
        if self.FOREGROUND_LOCK:
            self.prepare_foreground_lock()

        self.state = {}
        self.approot = None
        self.root = self.get_root()
        self.rebuild(first=True)

        if self.IDLE_DETECTION:
            self.install_idle(timeout=self.IDLE_TIMEOUT)

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
            path = realpath(path)
            Builder.unload_file(path)
        for name, module in self.CLASSES.items():
            Factory.unregister(name)

    def load_app_dependencies(self):
        """
        Load all the application dependencies.
        This is called before rebuild.
        """
        for path in self.KV_FILES:
            path = realpath(path)
            Builder.load_file(path)
        for name, module in self.CLASSES.items():
            Factory.register(name, module=module)

    def rebuild(self, *largs, **kwargs):
        Logger.debug("Reloader: Rebuild the application")
        first = kwargs.get("first", False)
        try:
            if not first:
                self.unload_app_dependencies()

            # in case the loading fail in the middle of building a widget
            # there will be existing rules context that will break later
            # instanciation. just clean it.
            Builder.rulectx = {}

            self.load_app_dependencies()
            self.set_widget(None)
            self.approot = self.build_app()
            self.set_widget(self.approot)
            self.apply_state(self.state)
        except Exception as e:
            import traceback
            Logger.exception("Reloader: Error when building app")
            self.set_error(repr(e), traceback.format_exc())
            if not self.DEBUG and self.RAISE_ERROR:
                raise

    @mainthread
    def set_error(self, exc, tb=None):
        from kivy.core.window import Window
        lbl = Factory.Label(
            size_hint = (1, None),
            padding_y = 150,
            text_size = (Window.width - 100, None),
            text="{}\n\n{}".format(exc, tb or ""))
        lbl.texture_update()
        lbl.height = lbl.texture_size[1]
        sv = Factory.ScrollView(
            size_hint = (1, 1),
            pos_hint = {'x': 0, 'y': 0},
            do_scroll_x = False,
            scroll_y = 0)
        sv.add_widget(lbl)
        self.set_widget(sv)

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
            Logger.warn("Reloader: Unavailable, watchdog is not installed")
            return
        Logger.info("Reloader: Autoreloader activated")
        rootpath = self.get_root_path()
        self.w_handler = handler = FileSystemEventHandler()
        handler.dispatch = self._reload_from_watchdog
        self._observer = observer = Observer()
        for path in self.AUTORELOADER_PATHS:
            options = {"recursive": True}
            if isinstance(path, (tuple, list)):
                path, options = path
            observer.schedule(
                handler, join(rootpath, path),
                **options)
        observer.start()

    @mainthread
    def _reload_from_watchdog(self, event):
        from watchdog.events import FileModifiedEvent
        if not isinstance(event, FileModifiedEvent):
            return

        for pat in self.AUTORELOADER_IGNORE_PATTERNS:
            if fnmatch(event.src_path, pat):
                return

        Logger.trace(f"Reloader: Event received {event.src_path}")
        if event.src_path.endswith(".py"):
            # source changed, reload it
            try:
                Builder.unload_file(event.src_path)
                self._reload_py(event.src_path)
            except Exception as e:
                import traceback
                self.set_error(repr(e), traceback.format_exc())
                return

        Logger.debug(f"Reloader: Triggered by {event}")
        Clock.unschedule(self.rebuild)
        Clock.schedule_once(self.rebuild, 0.1)

    def _reload_py(self, filename):
        # we don't have dependency graph yet, so if the module actually exists
        # reload it.

        filename = realpath(filename)

        # check if it's our own application file
        try:
            mod = sys.modules[self.__class__.__module__]
            mod_filename = realpath(mod.__file__)
        except Exception as e:
            mod_filename = None

        # detect if it's the application class // main
        if mod_filename == filename:
            return self._restart_app(mod)

        module = self._filename_to_module(filename)
        if module in sys.modules:
            Logger.debug("Reloader: Module exist, reload it")
            Factory.unregister_from_filename(filename)
            self._unregister_factory_from_module(module)
            reload(sys.modules[module])

    def _unregister_factory_from_module(self, module):
        # check module directly
        to_remove = [
            x for x in Factory.classes
            if Factory.classes[x]["module"] == module]

        # check class name
        for x in Factory.classes:
            cls = Factory.classes[x]["cls"]
            if not cls:
                continue
            if getattr(cls, "__module__", None) == module:
                to_remove.append(x)

        for name in set(to_remove):
            del Factory.classes[name]

    def _filename_to_module(self, filename):
        orig_filename = filename
        rootpath = self.get_root_path()
        if filename.startswith(rootpath):
            filename = filename[len(rootpath):]
        if filename.startswith(os.path.sep):
            filename = filename[1:]
        module = filename[:-3].replace(os.path.sep, ".")
        Logger.debug(f"Reloader: Translated {orig_filename} to {module}")
        return module

    def _restart_app(self, mod):
        _has_execv = sys.platform != 'win32'
        cmd = [sys.executable] + original_argv
        if not _has_execv:
            import subprocess
            subprocess.Popen(cmd)
            sys.exit(0)
        else:
            try:
                os.execv(sys.executable, cmd)
            except OSError:
                os.spawnv(os.P_NOWAIT, sys.executable, cmd)
                os._exit(0)

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
            Logger.info("Kiosk: Foreground lock activated")
        except Exception:
            Logger.warn("Kiosk: No foreground lock available")

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
            Logger.exception("Idle: Cannot use idle detector, monotonic is missing")
        self.idle_timer = None
        self.idle_timeout = timeout
        self.idle_paused = False
        Logger.info(f"Idle: Install idle detector, {timeout} seconds")
        Clock.schedule_interval(self._check_idle, 1)
        self.root.bind(
            on_touch_down=self.rearm_idle,
            on_touch_up=self.rearm_idle)
        if self.IDLE_DETECTION_AUTO_START:
            self.rearm_idle()

    def _check_idle(self, *largs):
        if not hasattr(self, "idle_timer"):
            Logger.trace("Idle: Check aborted: no idle_timer installed")
            return
        if self.idle_paused:
            Logger.trace("Idle: Check paused, idle_paused is True")
            return
        if self.idle_timer is None:
            Logger.trace("Idle: Check aborted, idle_timer is None")
            return
        Logger.debug(f"Idle: Check: {monotonic() - self.idle_timer} > {self.idle_timeout}")
        if monotonic() - self.idle_timer > self.idle_timeout:
            Logger.debug(f"Idle: Trigger on_idle")
            self.idle_timer = None
            self.dispatch("on_idle")

    def rearm_idle(self, *largs):
        """
        Rearm the idle timer
        """
        Logger.debug("Idle: Rearm idle timer")
        if not hasattr(self, "idle_timer"):
            return
        if self.idle_timer is None and not self.idle_paused:
            Logger.debug("Idle: Trigger on_wakeup")
            self.dispatch("on_wakeup")
        self.idle_timer = monotonic()

    def stop_idle(self, *largs):
        """
        Pause idle timer
        """
        self.idle_paused = True

    def restart_idle(self, *largs):
        """
        Can be used after stop_idle to restart idle timer
        """
        self.idle_paused = False
        self.rearm_idle()

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
        if "filename" not in kwargs:
            from inspect import getframeinfo, stack
            caller = getframeinfo(stack()[1][0])
            kwargs["filename"] = caller.filename
        return Builder.orig_load_string(string, **kwargs)
