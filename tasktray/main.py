from functools import partial

import rox
from rox.options import Option

from traylib import ICON_THEME
from traylib.main import Main
from traylib.winitem_config import WinItemConfig

from tasktray import TaskTray
from tasktray.appitem_config import AppItemConfig
from tasktray.app import AppError
from tasktray.rox_app import ROXApp
from tasktray.desktop_app import DesktopApp

import wnck


class TaskTrayMain(Main):
    
    def __init__(self, app_factories=[ROXApp, DesktopApp]):
        Main.__init__(self, "TaskTray")
        try:
            wnck.set_client_type(wnck.CLIENT_TYPE_PAGER)
        except:
            pass
        self.__screen = wnck.screen_get_default()
        self.__screen.force_update()
        self.__app_factories = app_factories

    def init_options(self):
        Main.init_options(self)
        self.__o_all_workspaces = Option("all_workspaces", True)
        self.__o_arrow = Option("arrow", True)
        self.__o_themed_icons = Option("themed_icons", False)
        
    def init_config(self):
        Main.init_config(self)
        self.__win_config = WinItemConfig(
            all_workspaces=self.__o_all_workspaces.int_value, 
            arrow=self.__o_arrow.int_value,
        )

        self.__appitem_config = AppItemConfig(
            themed_icons=self.__o_themed_icons.int_value,
        )

        # TaskTray doesn't use the 'hidden' option, so make sure no icons get
        # hidden.
        self.icon_config.hidden = False

    def get_app_by_path(self, path):
        for app_factory in self.__app_factories:
            try:
                return app_factory(path)
            except AppError:
                pass
        return None

    def get_app_by_name(self, name):
        for app_factory in self.__app_factories:
            app = app_factory.from_name(name)
            if app is not None:
                return app
        return None

    def create_tray(self):
        return TaskTray(
            tray_config=self.tray_config,
            icon_config=self.icon_config,
            win_config=self.__win_config,
            appitem_config=self.__appitem_config,
            screen=self.__screen,
            get_app_by_path=self.get_app_by_path,
            get_app_by_name=self.get_app_by_name,
        )

    def options_changed(self):
        if self.__o_arrow.has_changed:
            self.__win_config.arrow = self.__o_arrow.int_value
        if self.__o_all_workspaces.has_changed:
            self.__win_config.all_workspaces = (
                self.__o_all_workspaces.int_value
            )
        if self.__o_themed_icons.has_changed:
            self.__appitem_config.themed_icons = (
                self.__o_themed_icons.int_value
            )

        Main.options_changed(self)

    win_config = property(lambda self : self.__win_config)
    appitem_config = property(lambda self : self.__appitem_config)
