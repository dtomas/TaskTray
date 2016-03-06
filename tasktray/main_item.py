from rox import get_local_path

from traylib.main_item import MainItem
from traylib.icons import ThemedIcon

from tasktray.app import AppError
from tasktray.appitem import AppItem


class TaskTrayMainItem(MainItem):

    def __init__(self, tray, tray_config, icon_config, win_config,
                 screen, get_app_by_path, get_app_by_name):
        MainItem.__init__(self, tray, tray_config, icon_config)
        self.__screen = screen
        self.__win_config = win_config
        self.__get_app_by_path = get_app_by_path
        self.__get_app_by_name = get_app_by_name
        self.__screen_signal_handlers = [
            screen.connect(
                "showing-desktop-changed", self.__showing_desktop_changed
            )
        ]
        self.__win_config_signal_handlers = [
            win_config.connect(
                "all-workspaces-changed",
                lambda win_config: self.changed("name")
            )
        ]
        self.connect("destroyed", self.__destroyed)


    # Signal callbacks

    def __destroyed(self, widget):
        for handler in self.__screen_signal_handlers:
            self.__screen.disconnect(handler)
        for handler in self.__win_config_signal_handlers:
            self.__win_config.disconnect(handler)

    def __showing_desktop_changed(self, screen):
        self.changed("icon", "name")


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
            app = self.__get_app_by_path(path)
            if app is None:
                continue
            has_item = False
            box = self.tray.get_box("appitems")
            for item in box.items:
                if item.app is not None and item.app.path == app.path:
                    has_item = True
                    break
            if has_item:
                continue
            appitem = AppItem(
                self.__win_config,
                self.__screen,
                self.__get_app_by_name,
                class_group=None,
                app=app,
                pinned=True,
            )
            self.tray.get_box("appitems").add_item(appitem)
