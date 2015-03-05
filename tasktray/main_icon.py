import gobject, rox, os

from traylib import *
from traylib.menu_icon import MenuIcon

ICON_THEME.append_search_path(os.path.join(rox.app_dir, 'icons'))


class MainIcon(MenuIcon):

    def __init__(self, tray, icon_config, tray_config):
        MenuIcon.__init__(self, tray, icon_config, tray_config)
        SCREEN.connect("showing-desktop-changed",
                       self.__showing_desktop_changed)
        tray.win_config.add_configurable(self)

    def __showing_desktop_changed(self, screen):
        self.update_icon()
        self.update_tooltip()

    def update_option_all_workspaces(self):
        self.update_tooltip()

    def click(self, time):
        SCREEN.toggle_showing_desktop(not SCREEN.get_showing_desktop())

    def mouse_wheel_up(self, time):
        self.tray.win_config.all_workspaces = True

    def mouse_wheel_down(self, time):
        self.tray.win_config.all_workspaces = False

    def get_icon_names(self):
        if SCREEN.get_showing_desktop():
            return ["preferences-system-windows"]
        else:
            return ["user-desktop"]

    def make_tooltip(self):
        if SCREEN.get_showing_desktop():
            s = _("Click to show windows.\n")
        else:
            s = _("Click to show the desktop.\n")
        if self.tray.win_config.all_workspaces:
            s += _("Scroll down to only show windows of this workspace.")
        else:
            s += _("Scroll up to show windows of all workspaces.")
        #s += _("Right click will open the TaskTray menu.")
        return s
