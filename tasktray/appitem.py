import os

import gtk
from ConfigParser import SafeConfigParser, NoOptionError
from urllib import pathname2url

import rox
from rox import AppInfo, processes, filer
from rox.basedir import xdg_data_dirs

from traylib import APPDIRPATH, TARGET_URI_LIST
from traylib.winitem import AWindowsItem
from traylib.icons import ThemedIcon, PixbufIcon


class AppItem(AWindowsItem):

    def __init__(self, win_config, appitem_config, class_group, screen):
        AWindowsItem.__init__(self, win_config, screen)
        self.__appitem_config = appitem_config
        self.__class_group = class_group
        self.__screen = screen

        self.__update_app()

        self.__class_group_handlers = [
            self.__class_group.connect("name_changed", self.__name_changed),
        ]

        self.__screen_handlers = [
            screen.connect(
                "showing-desktop-changed", self.__showing_desktop_changed
            ),
            screen.connect("window-opened", self.__window_opened),
            screen.connect("window-closed", self.__window_closed),
            screen.connect(
                "class-group-closed", self.__class_group_closed
            ),
        ]

        for window in screen.get_windows():
            if window.get_class_group() is class_group:
                self.__window_opened(screen, window)

        self.connect(
            "visible-window-items-changed", self.__visible_window_items_changed
        )
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

    def __visible_window_items_changed(self, item):
        self.emit("icon-changed")
        self.emit("name-changed")

    def __class_group_closed(self, screen, class_group):
        if class_group is self.__class_group:
            self.destroy()

    def __themed_icons_changed(self, appitem_config):
        self.emit("icon-changed")

    def __name_changed(self, class_group):
        self.__update_app()
        self.emit("base-name-changed")
        self.emit("icon-changed")
        self.emit("menu-right-changed")
        self.emit("drag-source-changed")

    def __window_opened(self, screen, window):
        if window.get_class_group() is self.__class_group:
            self.add_window(window)

    def __window_closed(self, screen, window):
        self.remove_window(window)

    def __showing_desktop_changed(self, screen):
        self.emit("is-visible-changed")

    def __show_help(self, menu_item):
        filer.open_dir(os.path.join(self.__help_dir))    

    def __run_with_option(self, menu_item, option):
        """Runs the given appdir with the given option.""" 
        processes.PipeThroughCommand(
            (os.path.join(self.__app_dir, 'AppRun'), option), None, None
        ).start()

    def __run_desktop_option(self, menu_item, exec_):
        processes.PipeThroughCommand(exec_.split(' '), None, None).start()


    # Private methods:

    def __update_app(self):
        self.__app_dir = None
        self.__help_dir = None
        self.__app_options = []
        self.__desktop_file = None
        self.__icon_name = None

        appnames = (
            self.__class_group.get_name(), self.__class_group.get_res_class()
        )

        for appname in appnames:
            if self.__app_dir is None:
                for path in APPDIRPATH:
                    if not path:
                        continue
                    app_dir = os.path.join(path, appname)
                    if not os.path.isdir(app_dir):
                        app_dir = os.path.join(path, appname.capitalize())
                    if not os.path.isdir(app_dir):
                        app_dir = os.path.join(path, appname.upper())
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

            if self.__help_dir is None:
                for datadir in xdg_data_dirs:
                    help_dir = os.path.join(datadir, 'doc', appname.lower())
                    if os.path.isdir(help_dir):
                        self.__help_dir = help_dir
                        break

            if self.__app_dir is None and self.__desktop_file is None:
                for datadir in xdg_data_dirs:
                    applications_dir = os.path.join(datadir, "applications")
                    for leafname in appname, appname.lower(), appname.capitalize():
                        desktop_file = os.path.join(
                            applications_dir, leafname + ".desktop"
                        )
                        if os.path.exists(desktop_file):
                            self.__desktop_file = desktop_file
                            break
                    if self.__desktop_file is not None:
                        break

        if self.__desktop_file is not None:
            parser = SafeConfigParser()
            parser.read([self.__desktop_file])
            try:
                self.__icon_name = parser.get("Desktop Entry", "Icon")
            except NoOptionError:
                pass
            for section in parser.sections():
                if not section.startswith("Desktop Action"):
                    continue
                self.__app_options.append({
                    "label": parser.get(section, "Name"),
                    "exec": parser.get(section, "Exec"),
                })


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
            if 'option' in option:
                item.connect(
                    "activate", self.__run_with_option, option.get('option')
                )
            elif 'exec' in option:
                item.connect(
                    "activate", self.__run_desktop_option, option.get('exec')
                )
            stock_id = option.get('icon')
            if stock_id:
                item.get_image().set_from_stock(stock_id, gtk.ICON_SIZE_MENU)
            menu.prepend(item)
        return menu
    
    def get_icons(self):
        if self.__icon_name is not None:
            icons = [ThemedIcon(self.__icon_name)]
        else:
            icons = []
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
            icons += [ThemedIcon(icon_name) for icon_name in icon_names]
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

    def get_drag_source_targets(self):
        if self.__desktop_file is None and self.__app_dir is None:
            return AWindowsItem.get_drag_source_targets(self)
        return AWindowsItem.get_drag_source_targets(self) + [
            ("text/uri-list", 0, TARGET_URI_LIST)
        ]

    def get_drag_source_actions(self):
        if self.__desktop_file is None and self.__app_dir is None:
            return AWindowsItem.get_drag_source_actions(self)
        return (
            AWindowsItem.get_drag_source_actions(self) |
            gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_LINK
        )

    def drag_data_get(self, context, data, info, time):
        AWindowsItem.drag_data_get(self, context, data, info, time)
        if info == TARGET_URI_LIST:
            paths = []
            if self.__app_dir is not None:
                paths.append(self.__app_dir)
            if self.__desktop_file is not None:
                paths.append(self.__desktop_file)
            data.set_uris(['file://%s' % pathname2url(path) for path in paths])



    # AWindowsItem implementation:

    def get_base_name(self):
        return self.__class_group.get_name()
