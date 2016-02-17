from functools import partial

from rox import tasks

from traylib.tray_config import TrayConfig
from traylib.managed_tray import ManagedTray
from traylib.icon import IconConfig

from tasktray.appicon_manager import manage_appicons
from tasktray.main_icon import MainIcon


class TaskTray(ManagedTray):

    def __init__(self, icon_config, tray_config, win_config, appicon_config,
                 screen):
        self.__win_config = win_config
        self.__appicon_config = appicon_config
        self.__screen = screen

        ManagedTray.__init__(
            self, icon_config, tray_config,
            managers=[
                partial(
                    manage_appicons,
                    screen=screen,
                    icon_config=icon_config,
                    win_config=win_config,
                    appicon_config=appicon_config,
                )
            ],
            create_menu_icon=partial(
                MainIcon,
                win_config=win_config,
                screen=screen,
            ),
        )

    win_config = property(lambda self : self.__win_config)
    appicon_config = property(lambda self : self.__appicon_config)
    screen = property(lambda self : self.__screen)
