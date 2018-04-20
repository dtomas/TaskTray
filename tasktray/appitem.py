import os
from urllib.request import pathname2url

from gi.repository import GObject, Gtk, Gdk

from rox import filer

from traylib import TARGET_URI_LIST
from traylib.winitem import AWindowsItem
from traylib.icons import PixbufIcon

from tasktray.app import normalize_app_id


class AppItem(AWindowsItem):

    def __init__(self, win_config, screen, get_app_by_name, class_group=None,
                 app=None, pinned=False):
        assert class_group or app

        AWindowsItem.__init__(self, win_config, screen)
        self.__screen = screen
        self.__class_group = class_group
        self.__app = app
        self.__pinned = pinned
        self.__starting = False

        self.__class_group_handlers = []

        if class_group is not None and app is None:
            for name in self.__iter_app_ids_from_class_group(class_group):
                self.__app = get_app_by_name(name)
                if self.__app is not None:
                    break

        self.__screen_handlers = [
            screen.connect(
                "showing-desktop-changed", self.__showing_desktop_changed
            ),
            screen.connect(
                "class-group-closed", self.__class_group_closed
            ),
        ]

        self.connect("destroyed", self.__destroyed)

    # Signal callbacks:

    def __destroyed(self, item):
        for handler in self.__screen_handlers:
            self.__screen.disconnect(handler)
        if self.__class_group is not None:
            for handler in self.__class_group_handlers:
                self.__class_group.disconnect(handler)

    def _changed(self, props):
        props_to_emit = set()
        if "visible-window-items" in props:
            props_to_emit.update({
                "icon", "name", "is-greyed-out", "has-arrow", "zoom"
            })
            starting = self.__starting
            self.__starting = False
            if starting != self.__starting:
                props_to_emit.add("is-arrow-blinking")
        AWindowsItem._changed(self, props, props_to_emit)

    def offer_window_item(self, window_item):
        class_group = window_item.window.get_class_group()
        if class_group is None:
            return False
        if (self.__class_group is not None and
                self.__class_group is class_group):
            self.add_window_item(window_item)
            return True
        if self.__app is None:
            return False
        app_ids = list(self.__iter_app_ids_from_class_group(class_group))
        my_app_id = normalize_app_id(self.__app.id)
        for app_id in app_ids:
            if my_app_id == normalize_app_id(app_id):
                self.add_window_item(window_item)
                return True
        return False

    def __class_group_closed(self, screen, class_group):
        if class_group is self.__class_group:
            self.__class_group = None
            if self.__app is None or not self.__pinned:
                self.destroy()

    def __showing_desktop_changed(self, screen):
        self.changed("is-visible")

    def __show_help(self, menu_item):
        filer.open_dir(os.path.join(self.__app.help_dir))

    def __exec_option(self, menu_item, option):
        option.execute()

    # Private methods:

    def __iter_app_ids_from_class_group(self, class_group):
        name = class_group.get_res_class()
        if name is None:
            name = class_group.get_name()
        parts = name.split('-')
        for i in range(len(parts), 0, -1):
            name = '-'.join(parts[0:i])
            yield name


    # Item implementation:

    def get_menu_left(self):
        if len(self.visible_window_items) == 1:
            return None
        menu = AWindowsItem.get_menu_left(self)
        if self.__app is None:
            return menu

        #if menu is None:
        #    return None
        #menu.append(Gtk.SeparatorMenuItem())

        #def run(item):
        #    self.app.run()
        #item = Gtk.ImageMenuItem(Gtk.STOCK_EXECUTE)
        #item.connect("activate", run)
        #menu.append(item)
        return menu

    def get_menu_right(self):
        menu = AWindowsItem.get_menu_right(self)
        if self.__app is None:
            return menu
        if menu is None:
            menu = Gtk.Menu()
        else:
            menu.prepend(Gtk.SeparatorMenuItem())
            menu.prepend(Gtk.SeparatorMenuItem())
        if not self.__pinned:
            def pin(item):
                self.__pinned = True
                self.changed("is-visible")
                self.emit("pinned")
            item = Gtk.ImageMenuItem(_("Pin to TaskTray"))
            item.set_image(
                Gtk.Image.new_from_stock(Gtk.STOCK_ADD, Gtk.IconSize.MENU)
            )
            item.connect("activate", pin)
            menu.prepend(item)
        else:
            def unpin(item):
                self.__pinned = False
                self.changed("is-visible")
                self.emit("unpinned")
                if self.__class_group is None:
                    self.destroy()
            item = Gtk.ImageMenuItem(_("Remove from TaskTray"))
            item.set_image(
                Gtk.Image.new_from_stock(Gtk.STOCK_REMOVE, Gtk.IconSize.MENU)
            )
            item.connect("activate", unpin)
            menu.prepend(item)
        if self.__app.help_dir or self.__app.actions:
            menu.prepend(Gtk.SeparatorMenuItem())
        if self.__app.help_dir is not None:
            item = Gtk.ImageMenuItem.new_from_stock(Gtk.STOCK_HELP, None)
            menu.prepend(item)
            item.connect("activate", self.__show_help)
        for option in self.__app.actions:
            item = Gtk.ImageMenuItem(option.label)
            item.connect("activate", self.__exec_option, option)
            stock_id = option.stock_icon
            if stock_id:
                item.set_image(
                    Gtk.Image.new_from_stock(stock_id, Gtk.IconSize.MENU)
                )
            menu.prepend(item)
        menu.prepend(Gtk.SeparatorMenuItem())

        def run(item):
            self.run()
        item = Gtk.ImageMenuItem.new_from_stock(Gtk.STOCK_EXECUTE, None)
        item.connect("activate", run)
        menu.prepend(item)
        return menu

    def get_icons(self):
        if self.__app is not None and self.__app.icons:
            icons = list(self.__app.icons)
        else:
            icons = []
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
            return not self.__pinned
        return AWindowsItem.is_greyed_out(self)

    def get_zoom(self):
        if not self.visible_window_items:
            return 1.0
        return AWindowsItem.get_zoom(self)

    def get_drag_source_targets(self):
        if self.__app is None:
            return AWindowsItem.get_drag_source_targets(self)
        return AWindowsItem.get_drag_source_targets(self) + [
            Gtk.TargetEntry.new("text/uri-list", 0, TARGET_URI_LIST)
        ]

    def get_drag_source_actions(self):
        if self.__app is None:
            return AWindowsItem.get_drag_source_actions(self)
        return (
            AWindowsItem.get_drag_source_actions(self) |
            Gdk.DragAction.COPY | Gdk.DragAction.LINK
        )

    def drag_data_get(self, context, data, info, time):
        AWindowsItem.drag_data_get(self, context, data, info, time)
        if info == TARGET_URI_LIST:
            if self.__app is not None:
                data.set_uris(['file://%s' % pathname2url(self.__app.path)])

    def click(self, time=0):
        visible_window_items = self.visible_window_items
        if len(visible_window_items) == 0 and self.__app is not None:
            self.run()
            return True
        return AWindowsItem.click(self, time)

    def uris_dropped(self, uri_list, action):
        if self.__app is not None:
            self.run(uri_list)

    def is_drop_target(self):
        return self.__app is not None and self.__app.is_drop_target

    def is_arrow_blinking(self):
        return self.__starting

    def spring_open(self, time=0):
        if self.__app is not None and not self.visible_window_items:
            self.run()
            return False
        else:
            return AWindowsItem.spring_open(self, time)


    # AWindowsItem implementation:

    def get_base_name(self):
        if self.__class_group is not None:
            return self.__class_group.get_name()
        if self.__app is not None:
            return self.__app.name
        return None

    # Public methods:

    def run(self, uri_list=()):
        self.__starting = True
        self.changed("is-arrow-blinking")
        self.__app.run(uri_list)

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


GObject.signal_new(
    "pinned", AppItem, GObject.SignalFlags.RUN_FIRST, GObject.TYPE_NONE, ()
)
GObject.signal_new(
    "unpinned", AppItem, GObject.SignalFlags.RUN_FIRST, GObject.TYPE_NONE, ()
)
