from functools import partial

from rox import tasks

from traylib.tray_config import TrayConfig
from traylib.managed_tray import ManagedTray
from traylib.icon import IconConfig

from tasktray.appitem_manager import manage_appitems
from tasktray.main_item import TaskTrayMainItem


class TaskTray(ManagedTray):

    def __init__(self, icon_config, tray_config, win_config, appitem_config,
                 screen):
        self.__win_config = win_config
        self.__appitem_config = appitem_config
        self.__screen = screen

        ManagedTray.__init__(
            self, icon_config, tray_config,
            managers=[
                partial(
                    manage_appitems,
                    screen=screen,
                    icon_config=icon_config,
                    win_config=win_config,
                    appitem_config=appitem_config,
                )
            ],
            create_main_item=partial(
                TaskTrayMainItem,
                win_config=win_config,
                screen=screen,
            ),
        )

    win_config = property(lambda self : self.__win_config)
    appitem_config = property(lambda self : self.__appitem_config)
    screen = property(lambda self : self.__screen)
