from functools import partial

import rox
from rox.options import Option

from traylib import ICON_THEME
from traylib.main import Main
from traylib.winitem_config import WinItemConfig

from tasktray import TaskTray
from tasktray.appitem_config import AppItemConfig

import wnck


class TaskTrayMain(Main):
    
    def __init__(self):
        Main.__init__(self, "TaskTray")
        try:
            wnck.set_client_type(wnck.CLIENT_TYPE_PAGER)
        except:
            pass
        self.__screen = wnck.screen_get_default()
        self.__screen.force_update()

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

    def create_tray(self):
        return TaskTray(
            tray_config=self.tray_config,
            icon_config=self.icon_config,
            win_config=self.__win_config,
            appitem_config=self.__appitem_config,
            screen=self.__screen,
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
