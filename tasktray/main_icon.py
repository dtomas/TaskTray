from traylib.menu_icon import MenuIcon


class MainIcon(MenuIcon):

    def __init__(self, tray, win_config, screen):
        MenuIcon.__init__(self, tray)
        self.__screen = screen
        self.__win_config = win_config
        screen.connect(
            "showing-desktop-changed", self.__showing_desktop_changed
        )
        win_config.connect(
            "all-workspaces-changed", lambda win_config: self.update_tooltip()
        )

    def __showing_desktop_changed(self, screen):
        self.update_icon()
        self.update_tooltip()


    # Methods inherited from Icon.

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

    def make_tooltip(self):
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
