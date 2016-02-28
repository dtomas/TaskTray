from rox import get_local_path

from traylib.main_item import MainItem
from traylib.icons import ThemedIcon

from tasktray.app import AppError
from tasktray.rox_app import ROXApp
from tasktray.desktop_app import DesktopApp
from tasktray.appitem import AppItem


class TaskTrayMainItem(MainItem):

    def __init__(self, tray, win_config, appitem_config, screen):
        MainItem.__init__(self, tray)
        self.__screen = screen
        self.__win_config = win_config
        self.__appitem_config = appitem_config
        self.__screen_signal_handlers = [
            screen.connect(
                "showing-desktop-changed", self.__showing_desktop_changed
            )
        ]
        self.__win_config_signal_handlers = [
            win_config.connect(
                "all-workspaces-changed",
                lambda win_config: self.emit("name-changed")
            )
        ]
        self.connect("destroyed", self.__destroyed)


    # Signal callbacks

    def __showing_desktop_changed(self, screen):
        self.emit("icon-changed")
        self.emit("name-changed")

    def __destroyed(self, widget):
        for handler in self.__screen_signal_handlers:
            self.__screen.disconnect(handler)
        for handler in self.__win_config_signal_handlers:
            self.__win_config.disconnect(handler)


    # Methods inherited from Item.

    def click(self, time):
        self.__screen.toggle_showing_desktop(
            not self.__screen.get_showing_desktop()
        )

    def mouse_wheel_up(self, time):
        self.__win_config.all_workspaces = True

    def mouse_wheel_down(self, time):
        self.__win_config.all_workspaces = False

    def get_icons(self):
        if self.__screen.get_showing_desktop():
            return [ThemedIcon("preferences-system-windows")]
        else:
            return [ThemedIcon("user-desktop")]

    def get_name(self):
        if self.__screen.get_showing_desktop():
            s = _("Click to show windows.\n")
        else:
            s = _("Click to show the desktop.\n")
        if self.__win_config.all_workspaces:
            s += _("Scroll down to only show windows of this workspace.")
        else:
            s += _("Scroll up to show windows of all workspaces.")
        #s += _("Right click will open the TaskTray menu.")
        return s

    def is_drop_target(self):
        return True

    def uris_dropped(self, uri_list, action):
        for uri in uri_list:
            path = get_local_path(uri)
            if not path:
                continue
            try:
                app = ROXApp(path)
            except AppError:
                try:
                    app = DesktopApp(path)
                except AppError:
                    continue
            has_item = False
            for item in self.tray.items:
                if item.app is not None and item.app.path == app.path:
                    has_item = True
                    break
            if has_item:
                continue
            appitem = AppItem(
                self.__win_config,
                self.__appitem_config,
                self.__screen,
                class_group=None,
                app=app,
                pinned=True,
            )
            self.tray.add_item(None, appitem)
