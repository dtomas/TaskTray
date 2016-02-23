from traylib.main_item import MainItem


class TaskTrayMainItem(MainItem):

    def __init__(self, tray, win_config, screen):
        MainItem.__init__(self, tray)
        self.__screen = screen
        self.__win_config = win_config
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
        #self.connect("destroy", self.__destroy)


    # Signal callbacks

    def __showing_desktop_changed(self, screen):
        self.emit("icon-changed")
        self.emit("name-changed")

    def __destroy(self, widget):
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

    def get_icon_names(self):
        if self.__screen.get_showing_desktop():
            return ["preferences-system-windows"]
        else:
            return ["user-desktop"]

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
