import os
from urllib import pathname2url

import gobject
import gtk

import rox
from rox import processes, filer

from traylib import TARGET_URI_LIST
from traylib.winitem import AWindowsItem
from traylib.icons import ThemedIcon, PixbufIcon

from tasktray.rox_app import ROXApp
from tasktray.desktop_app import DesktopApp


class AppItem(AWindowsItem):

    def __init__(self, win_config, appitem_config, screen, class_group=None,
                 app=None, pinned=False):
        assert class_group or app

        AWindowsItem.__init__(self, win_config, screen)
        self.__appitem_config = appitem_config
        self.__screen = screen
        self.__class_group = class_group
        self.__app = app
        self.__pinned = pinned

        self.__class_group_handlers = []
        self.__update_class_group()

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
        if self.__class_group is not None:
            for handler in self.__class_group_handlers:
                self.__class_group.disconnect(handler)

    def __visible_window_items_changed(self, item):
        self.emit("icon-changed")
        self.emit("name-changed")
        self.emit("is-greyed-out-changed")
        self.emit("has-arrow-changed")
        self.emit("zoom-changed")

    def offer_class_group(self, class_group):
        self.__update_class_group()
        return class_group is self.__class_group

    def __class_group_closed(self, screen, class_group):
        if class_group is self.__class_group:
            self.__class_group = None
            if self.__app is None:
                self.destroy()
            else:
                self.__update_class_group()
                if not self.__pinned:
                    self.destroy()

    def __themed_icons_changed(self, appitem_config):
        self.emit("icon-changed")

    def __window_opened(self, screen, window):
        if (self.__class_group is not None and
                window.get_class_group() is self.__class_group):
            self.add_window(window)

    def __window_closed(self, screen, window):
        self.remove_window(window)

    def __showing_desktop_changed(self, screen):
        self.emit("is-visible-changed")

    def __show_help(self, menu_item):
        filer.open_dir(os.path.join(self.__app.help_dir))

    def __exec_option(self, menu_item, option):
        option.execute()


    # Private methods:

    def __app_ids_from_class_group(self, class_group):
        for name in [class_group.get_name(), class_group.get_res_class()]:
            parts = name.split('-')
            for i in range(1, len(parts) + 1):
                name = '-'.join(parts[0 : i]) 
                yield name
                yield name.lower()

    def __update_class_group(self):
        if self.__class_group is None:
            class_groups = set()
            for window in self.__screen.get_windows():
                class_groups.add(window.get_class_group())
            for class_group in class_groups:
                for app_id in self.__app_ids_from_class_group(class_group):
                    if self.__app.id == app_id:
                        self.__class_group = class_group
                        break
                if self.__class_group is not None:
                    break

        if self.__class_group is not None and self.__app is None:
            for name in self.__app_ids_from_class_group(self.__class_group):
                self.__app = ROXApp.from_name(name)
                if self.__app is None:
                    self.__app = DesktopApp.from_name(name)
                if self.__app is not None:
                    break

        self.emit("base-name-changed")
        self.emit("name-changed")
        self.emit("zoom-changed")


    # Item implementation:

    def get_menu_right(self):
        menu = AWindowsItem.get_menu_right(self)
        if self.__app is None:
            return menu
        if not menu:
            menu = gtk.Menu()
        else:
            menu.prepend(gtk.SeparatorMenuItem())
            menu.prepend(gtk.SeparatorMenuItem())
        if not self.__pinned:
            def pin(item):
                self.__pinned = True
                self.emit("is-visible-changed")
                self.emit("pinned")
            item = gtk.ImageMenuItem(_("Permanently add to TaskTray."))
            item.get_image().set_from_stock(
                gtk.STOCK_ADD, gtk.ICON_SIZE_MENU
            )
            item.connect("activate", pin)
            menu.prepend(item)
        else:
            def unpin(item):
                self.__pinned = False
                self.emit("is-visible-changed")
                self.emit("unpinned")
                if self.__class_group is None:
                    self.destroy()
            item = gtk.ImageMenuItem(_("Remove from TaskTray."))
            item.get_image().set_from_stock(
                gtk.STOCK_REMOVE, gtk.ICON_SIZE_MENU
            )
            item.connect("activate", unpin)
            menu.prepend(item)
        if self.__app.help_dir or self.__app.options:
            menu.prepend(gtk.SeparatorMenuItem())
        if self.__app.help_dir is not None:
            item = gtk.ImageMenuItem(gtk.STOCK_HELP)
            menu.prepend(item)
            item.connect("activate", self.__show_help)
        for option in self.__app.options:
            item = gtk.ImageMenuItem(option.label)
            item.connect("activate", self.__exec_option, option)
            stock_id = option.stock_icon
            if stock_id:
                item.get_image().set_from_stock(stock_id, gtk.ICON_SIZE_MENU)
            menu.prepend(item)
        return menu
    
    def get_icons(self):
        if self.__app is not None and self.__app.icons:
            icons = self.__app.icons
        else:
            icons = []
        if self.__appitem_config.themed_icons:
            icon_names = set()
            for window_item in self.visible_window_items:
                app = window_item.window.get_application()
                if app is None or app.get_icon_is_fallback():
                    continue
                icon_names.add(app.get_icon_name())
            if self.__class_group is not None:
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

    def has_arrow(self):
        return bool(self.visible_window_items)

    def is_visible(self):
        return (
            not self.__screen.get_showing_desktop() and
            AWindowsItem.is_visible(self) or self.__pinned
        )

    def is_greyed_out(self):
        if not self.visible_window_items:
            return True
        return AWindowsItem.is_greyed_out(self)

    def get_zoom(self):
        if not self.visible_window_items:
            return 1.0
        return AWindowsItem.get_zoom(self)

    def get_name(self):
        visible_window_items = self.visible_window_items
        if not visible_window_items:
            return self.get_base_name()
        if len(visible_window_items) == 1:
            return visible_window_items[0].get_name()
        return AWindowsItem.get_name(self)

    def get_drag_source_targets(self):
        if self.__app is None:
            return AWindowsItem.get_drag_source_targets(self)
        return AWindowsItem.get_drag_source_targets(self) + [
            ("text/uri-list", 0, TARGET_URI_LIST)
        ]

    def get_drag_source_actions(self):
        if self.__app is None:
            return AWindowsItem.get_drag_source_actions(self)
        return (
            AWindowsItem.get_drag_source_actions(self) |
            gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_LINK
        )

    def drag_data_get(self, context, data, info, time):
        AWindowsItem.drag_data_get(self, context, data, info, time)
        if info == TARGET_URI_LIST:
            if self.__app is not None:
                data.set_uris(['file://%s' % pathname2url(self.__app.path)])

    def click(self, time=0L):
        visible_window_items = self.visible_window_items
        if len(visible_window_items) == 0 and self.__app is not None:
            self.__app.run()
            return True
        return AWindowsItem.click(self, time)


    # AWindowsItem implementation:

    def get_base_name(self):
        if self.__class_group is not None:
            return self.__class_group.get_name()
        if self.__app is not None:
            return self.__app.name
        return None

    
    # Properties:

    @property
    def app(self):
        return self.__app

    @property
    def is_pinned(self):
        """
        C{True} if the item will stay in the tray even if its windows are
        closed.
        """
        return self.__pinned


gobject.signal_new(
    "pinned", AppItem, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ()
)
gobject.signal_new(
    "unpinned", AppItem, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ()
)
