import os
import json

from rox.basedir import xdg_config_home
from traylib.item_box import ItemBox

from tasktray.appitem import AppItem
from tasktray.app import AppError
from tasktray.rox_app import ROXApp
from tasktray.desktop_app import DesktopApp


def manage_appitems(tray, screen, icon_config, win_config, get_app_by_path,
                    get_app_by_name):

    class state:
        initializing = True
        box = None
        screen_handlers = []
        box_handlers = []

    def get_pinned_items_path():
        return os.path.join(
            xdg_config_home, "dtomas", "TaskTray", "pinned-icons.json"
        )

    def save_pinned_items(*args):
        pinned_items = []
        for item in state.box.items:
            if item.app is not None and item.is_pinned:
                pinned_items.append(item.app.path)
        with open(get_pinned_items_path(), "w") as f:
            json.dump(pinned_items, f)

    def window_opened(screen, window):
        for item in state.box.items:
            if item.offer_window(window):
                return
        if window.get_class_group() is None:
            return
        appitem = AppItem(
            win_config, screen, get_app_by_name,
            window.get_class_group(),
        )
        appitem.connect("pinned", save_pinned_items)
        appitem.connect("unpinned", save_pinned_items)
        appitem.add_window(window)
        state.box.add_item(appitem)

    def manage():
        state.box = ItemBox("appitems")
        tray.add_box(state.box)
        pinned_items_path = get_pinned_items_path()
        if os.path.exists(pinned_items_path):
            with open(pinned_items_path, "r") as f:
                pinned_items = json.load(f)
            for path in pinned_items:
                yield None
                app = get_app_by_path(path)
                if app is None:
                    continue
                appitem = AppItem(
                    win_config,
                    screen,
                    get_app_by_name,
                    class_group=None,
                    app=app,
                    pinned=True,
                )
                state.box.add_item(appitem)
        for window in screen.get_windows():
            window_opened(screen, window)
            yield None
        state.screen_handlers = [
            screen.connect("window-opened", window_opened),
        ]
        state.box_handlers = [
            state.box.connect("item-added", item_added),
            state.box.connect("item-reordered", save_pinned_items),
        ]
        state.initializing = False

    def unmanage():
        for handler in state.screen_handlers:
            screen.disconnect(handler)
            yield None
        for handler in state.box_handlers:
            state.box.disconnect(handler)
            yield None
        state.box.destroy()
        state.box = None
        state.screen_handlers = []
        state.box_handlers = []

    def item_added(box, item):
        if not state.initializing:
            save_pinned_items(item)
        item.connect("pinned", save_pinned_items)
        item.connect("unpinned", save_pinned_items)

    return manage, unmanage
