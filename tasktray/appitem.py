import os

import gtk

import rox
from rox import AppInfo, processes, filer
from rox.basedir import xdg_data_dirs

from traylib import APPDIRPATH
from traylib.winitem import AWindowsItem
from traylib.icons import ThemedIcon, PixbufIcon


class AppItem(AWindowsItem):

    def __init__(self, win_config, appitem_config, class_group, screen):
        AWindowsItem.__init__(self, win_config, screen)
        self.__appitem_config = appitem_config
        self.__class_group = class_group
        self.__screen = screen

        self.__app_dir = None
        self.__help_dir = None
        self.__app_options = []

        dirname = self.__class_group.get_name()
        if dirname:
            for path in APPDIRPATH:
                if not path:
                    continue
                app_dir = os.path.join(path, dirname)
                if not os.path.isdir(app_dir):
                    app_dir = os.path.join(path, dirname.capitalize())
                if not os.path.isdir(app_dir):
                    app_dir = os.path.join(path, dirname.upper())
                if rox.isappdir(app_dir):
                    self.__app_dir = app_dir
                    help_dir = os.path.join(app_dir, 'Help')
                    if os.path.isdir(help_dir):
                        self.__help_dir = help_dir
                    app_info = os.path.join(app_dir, 'AppInfo.xml')
                    if os.access(app_info, os.R_OK):
                        self.__app_options = (
                            AppInfo.AppInfo(app_info).getAppMenu()
                        )
                        break
            if not self.__help_dir:
                for datadir in xdg_data_dirs:
                    help_dir = os.path.join(datadir, 'doc', dirname.lower())
                    if os.path.isdir(help_dir):
                        self.__help_dir = help_dir
                        break

        self.__class_group_handlers = [
            self.__class_group.connect("name_changed", self.__name_changed),
        ]

        self.__screen_handlers = [
            self.__screen.connect(
                "showing-desktop-changed", self.__showing_desktop_changed
            ),
            self.__screen.connect("window-opened", self.__window_opened),
            self.__screen.connect("window-closed", self.__window_closed),
            self.__screen.connect(
                "class-group-closed", self.__class_group_closed
            ),
        ]

        for window in self.__screen.get_windows():
            if window.get_class_group() is class_group:
                self.__window_opened(screen, window)

        self.connect("destroyed", self.__destroyed)

        self.__appitem_config_handlers = [
            appitem_config.connect(
                "themed-icons-changed", self.__themed_icons_changed
            ),
        ]


    # Signal callbacks:

    def __destroyed(self, item):
        for handler in self.__screen_handlers:
            self.__screen.disconnect(handler)
        for handler in self.__appitem_config_handlers:
            self.__appitem_config.disconnect(handler)
        for handler in self.__class_group_handlers:
            self.__class_group.disconnect(handler)

    def __class_group_closed(self, screen, class_group):
        if class_group is self.__class_group:
            self.destroy()

    def __themed_icons_changed(self, appitem_config):
        self.emit("icon-changed")

    def __name_changed(self, class_group):
        self.emit("name-changed")
        self.emit("icon-changed")

    def __window_opened(self, screen, window):
        if window.get_class_group() is self.__class_group:
            self.add_window(window)

    def __window_closed(self, screen, window):
        self.remove_window(window)
        self.emit("name-changed")

    def __showing_desktop_changed(self, screen):
        self.emit("is-visible-changed")

    def __show_help(self, menu_item):
        filer.open_dir(os.path.join(self.__help_dir))    

    def __run_with_option(self, menu_item, option):
        """Runs the given appdir with the given option.""" 
        processes.PipeThroughCommand(
            (os.path.join(self.__app_dir, 'AppRun'), option), None, None
        ).start()


    # Item implementation:

    def get_menu_right(self):
        menu = AWindowsItem.get_menu_right(self)
        if not self.__app_options and not self.__help_dir:
            return menu
        if not menu:
            menu = gtk.Menu()
        else:
            menu.prepend(gtk.SeparatorMenuItem())
            menu.prepend(gtk.SeparatorMenuItem())
        if self.__help_dir:
            item = gtk.ImageMenuItem(gtk.STOCK_HELP)
            menu.prepend(item)
            item.connect("activate", self.__show_help)
        for option in self.__app_options:
            item = gtk.ImageMenuItem(option.get('label'))
            item.connect(
                "activate", self.__run_with_option, option.get('option')
            )
            stock_id = option.get('icon')
            if stock_id:
                item.get_image().set_from_stock(stock_id, gtk.ICON_SIZE_MENU)
            menu.prepend(item)
        return menu
    
    def get_icons(self):
        if self.__appitem_config.themed_icons:
            icon_names = set()
            for window_item in self.visible_window_items:
                app = window_item.window.get_application()
                if app is None or app.get_icon_is_fallback():
                    continue
                icon_names.add(app.get_icon_name())
            icon_names = list(icon_names) + [
                self.__class_group.get_name().lower(),
                self.__class_group.get_res_class().lower()
            ]
            icons = [ThemedIcon(icon_name) for icon_name in icon_names]
        else:
            icons = []
        for window_item in self.visible_window_items:
            app = window_item.window.get_application()
            if app is None or app.get_icon_is_fallback():
                continue
            icons.append(PixbufIcon(app.get_icon()))
            break
        return icons

    def is_visible(self):
        return (
            not self.__screen.get_showing_desktop() and
            AWindowsItem.is_visible(self)
        )

    def get_name(self):
        visible_window_items = self.visible_window_items
        if len(visible_window_items) == 1:
            return visible_window_items[0].get_name()
        return AWindowsItem.get_name(self)


    # AWindowsItem implementation:

    def get_base_name(self):
        return self.__class_group.get_name()
