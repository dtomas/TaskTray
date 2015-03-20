import os
import struct

import gtk

import rox
from rox import processes, AppInfo, filer
from rox.basedir import xdg_data_dirs

from traylib import APPDIRPATH, TARGET_WNCK_WINDOW_ID
from traylib.winicon import WinIcon


class AppIcon(WinIcon):

    def __init__(self, icon_config, win_config, appicon_config, class_group,
                 screen):
        WinIcon.__init__(self, icon_config, win_config, screen)

        self.__appicon_config = appicon_config
        appicon_config.add_configurable(self)

        self.__class_group = class_group

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
                    app_dir = os.path.join(path,
                                           dirname[0].upper() + dirname[1:])
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
                            AppInfo.AppInfo(app_info).getAppMenu())
                        break
            if not self.__help_dir:
                for datadir in xdg_data_dirs:
                    help_dir = os.path.join(datadir, 'doc', dirname.lower())
                    if os.path.isdir(help_dir):
                        self.__help_dir = help_dir
                        break

        self.__class_group.connect("icon_changed", self.__icon_changed)
        self.__class_group.connect("name_changed", self.__name_changed)

        self.drag_source_set(gtk.gdk.BUTTON1_MASK, 
                            [("application/x-wnck-window-id", 
                                0,
                                TARGET_WNCK_WINDOW_ID)], 
                            gtk.gdk.ACTION_MOVE)
        self.connect("drag-data-get", self.__drag_data_get)
        
        self.connect("destroy", self.__destroy)
        self.screen.connect("showing-desktop-changed",
                       self.__showing_desktop_changed)
        
    def __showing_desktop_changed(self, screen):
        self.update_visibility()

    def __destroy(self, widget):
        self.__appicon_config.remove_configurable(self)

    def __drag_data_get(self, widget, context, data, info, time):
        xid = self.visible_windows[0].get_xid()
        data.set(data.target, 8, apply(struct.pack, ['1i', xid]))

    def __icon_changed(self, class_group):
        self.update_icon()

    def __name_changed(self, class_group):
        self.update_name()
        self.update_tooltip()
        self.update_icon()


    # Methods from WinIcon.

    def window_is_visible(self, window):
        return (WinIcon.window_is_visible(self, window) 
            and window.get_class_group() == self.__class_group)

    def should_have_window(self, window):
        return window.get_class_group() == self.__class_group


    # Methods from Icon.

    def get_menu_right(self):
        menu = WinIcon.get_menu_right(self)
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
            item.connect("activate", self.__run_with_option,
                         option.get('option'))
            stock_id = option.get('icon')
            if stock_id:
                item.get_image().set_from_stock(stock_id, gtk.ICON_SIZE_MENU)
            menu.prepend(item)
        return menu
    
    def get_icon_names(self):
        if not self.__appicon_config.themed_icons:
            return []
        return [self.__class_group.get_name().lower()]

    def get_icon_pixbuf(self):
        icon = self.icon
        for window in self.visible_windows:
            app = window.get_application()
            if app and not app.get_icon_is_fallback():
                icon = window.get_icon()
                if window.is_active():
                    break
        if not icon:
            icon = self.__class_group.get_icon()
        return icon

    def make_name(self):
        return self.__class_group.get_name()

    def make_tooltip(self):
        if not self.__class_group:
            return None
        visible_windows = self.visible_windows
        if len(visible_windows) == 1:
            window = visible_windows[0]
            name = window.get_name()
            if window.is_minimized():
                name = '[ ' + name + ' ]'
            if window.is_shaded():
                name = '= ' + name + ' ='
            if window.needs_attention():
                name = '!! ' + name + ' !!'
            return name
        return "%s (%d)" % (self.__class_group.get_name(), 
                            len(visible_windows))

    def make_visibility(self):
        return (
            not self.screen.get_showing_desktop() and
            WinIcon.make_visibility(self)
        )


    # Methods called when AppIconConfig has changed.

    def update_option_themed_icons(self):
        self.update_icon()

    
    # Methods for app options

    def __show_help(self, menu_item):
        filer.open_dir(os.path.join(self.__help_dir))    

    def __run_with_option(self, menu_item, option):
        """Runs the given appdir with the given option.""" 
        processes.PipeThroughCommand((os.path.join(self.__app_dir, 'AppRun'), 
                                        option), 
                                    None, None).start()
