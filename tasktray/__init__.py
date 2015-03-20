from functools import partial

from rox import tasks

from traylib.tray_config import TrayConfig
from traylib.managed_tray import ManagedTray
from traylib.icon import IconConfig
from traylib.winicon_manager import WinIconManager

from tasktray.appicon_manager import AppIconManager
from tasktray.main_icon import MainIcon


class TaskTray(ManagedTray):

    def __init__(self, icon_config, tray_config, win_config, appicon_config,
                 screen):
        self.__win_config = win_config
        self.__appicon_config = appicon_config
        self.__screen = screen

        ManagedTray.__init__(
            self, icon_config, tray_config,
            partial(
                AppIconManager,
                screen=screen,
                icon_config=icon_config,
                win_config=win_config,
                appicon_config=appicon_config
            ),
            MainIcon, win_config, screen
        )

    win_config = property(lambda self : self.__win_config)
    appicon_config = property(lambda self : self.__appicon_config)
    screen = property(lambda self : self.__screen)
