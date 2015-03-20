from traylib.winicon_manager import WinIconManager

from tasktray.appicon import AppIcon


class AppIconManager(WinIconManager):

    def __init__(self, tray, screen, icon_config, win_config, appicon_config):
        WinIconManager.__init__(self, tray, screen)
        self.__class_groups = {}
        self.__active_icon = None
        self.__icon_config = icon_config
        self.__win_config = win_config
        self.__appicon_config = appicon_config

    def init(self):
        self.tray.add_box(None)
        self.__window_opened_handler = (
            self.screen.connect("window-opened", self.__window_opened)
        )
        self.__window_closed_handler = (
            self.screen.connect("window-closed", self.__window_closed)
        )

        for window in self.screen.get_windows():
            self.__window_opened(self.screen, window)
            yield None

        for x in WinIconManager.init(self):
            yield None

    def quit(self):
        self.screen.disconnect(self.__window_opened_handler)
        self.screen.disconnect(self.__window_closed_handler)

        for x in WinIconManager.quit(self):
            yield None

    def __window_opened(self, screen, window):
        class_group = window.get_class_group()
        icon = self.tray.get_icon(class_group)
        if not icon:
            icon = AppIcon(self.__icon_config, 
                           self.__win_config,
                           self.__appicon_config,
                           class_group,
                           self.screen)
            icon.update_name()
            icon.update_icon()
            self.tray.add_icon(None, class_group, icon)
        self.__class_groups[window] = class_group

    def __window_closed(self, screen, window):
        class_group = self.__class_groups.get(window)
        if not class_group:
            return
        icon = self.tray.get_icon(class_group)
        if icon:
            if not icon.has_windows:
                self.tray.remove_icon(class_group)
            else:
                icon.update_icon()
        del self.__class_groups[window]
