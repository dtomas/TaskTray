from functools import partial

from rox import tasks

from traylib.tray_config import TrayConfig
from traylib.managed_tray import ManagedTray
from traylib.icon import IconConfig

from tasktray.appitem_manager import manage_appitems
from tasktray.main_item import TaskTrayMainItem


class TaskTray(ManagedTray):

    def __init__(self, tray_config, icon_config, win_config, screen,
                 get_app_by_path, get_app_by_name):
        self.__win_config = win_config
        self.__screen = screen

        ManagedTray.__init__(
            self,
            managers=[
                partial(
                    manage_appitems,
                    screen=screen,
                    icon_config=icon_config,
                    win_config=win_config,
                    get_app_by_path=get_app_by_path,
                    get_app_by_name=get_app_by_name,
                )
            ],
            create_main_item=partial(
                TaskTrayMainItem,
                tray_config=tray_config,
                icon_config=icon_config,
                win_config=win_config,
                screen=screen,
                get_app_by_path=get_app_by_path,
                get_app_by_name=get_app_by_name,
            ),
        )

    win_config = property(lambda self : self.__win_config)
    screen = property(lambda self : self.__screen)
