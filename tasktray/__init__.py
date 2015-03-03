import sys, os, rox

from traylib import *
from traylib.tray import Tray, TrayConfig
from traylib.icon import IconConfig

from tasktray.appicon import AppIcon
from tasktray.main_icon import MainIcon


class TaskTray(Tray):

    def __init__(self, icon_config, tray_config, win_config, appicon_config):
        self.__win_config = win_config
        self.__appicon_config = appicon_config
        self.__class_groups = {}
        self.__active_icon = None

        Tray.__init__(self, icon_config, tray_config, MainIcon)

        self.add_box(None)

        SCREEN.connect("window-opened", self.__window_opened)
        SCREEN.connect("window-closed", self.__window_closed)
        SCREEN.connect("active-window-changed", self.__active_window_changed)
        SCREEN.connect("active-workspace-changed", 
                        self.__active_workspace_changed)

        for window in SCREEN.get_windows():
            self.__window_opened(SCREEN, window)
        self.__active_window_changed(SCREEN)

    def __active_window_changed(self, screen, window = None):
        if self.__active_icon:
            self.__active_icon.update_zoom_factor()
            self.__active_icon.update_icon()
        window = screen.get_active_window()
        if window:
            icon = self.get_icon(window.get_class_group())
            if icon:
                icon.update_zoom_factor()
                icon.update_icon()
            self.__active_icon = icon
        else:
            self.__active_icon = None

    def __active_workspace_changed(self, screen, workspace = None):
        if self.__win_config.all_workspaces:
            return
        for icon in self.icons:
            icon.update_windows()

    def __window_opened(self, screen, window):
        class_group = window.get_class_group()
        icon = self.get_icon(class_group)
        if not icon:
            icon = AppIcon(self.icon_config, 
                            self.__win_config,
                            self.__appicon_config,
                            class_group)
            icon.update_name()
            icon.update_icon()
            self.add_icon(None, class_group, icon)
        icon.add_window(window)
        self.__class_groups[window] = class_group

    def __window_closed(self, screen, window):
        class_group = self.__class_groups.get(window)
        if not class_group:
            return
        icon = self.get_icon(class_group)
        if icon:
            icon.remove_window(window)
            if not icon.has_windows:
                self.remove_icon(class_group)
            else:
                icon.update_icon()
        del self.__class_groups[window]

    win_config = property(lambda self : self.__win_config)
    appicon_config = property(lambda self : self.__appicon_config)
