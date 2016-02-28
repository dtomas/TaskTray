import os
import json

from rox.basedir import xdg_config_home
from traylib.icon_renderer import render_icon

from tasktray.appitem import AppItem
from tasktray.app import AppError
from tasktray.rox_app import ROXApp
from tasktray.desktop_app import DesktopApp


def manage_appitems(tray, screen, icon_config, win_config, appitem_config):

    tray.add_box(None)

    class state:
        initializing = True

    def get_pinned_items_path():
        return os.path.join(
            xdg_config_home, "dtomas", "TaskTray", "pinned-icons.json"
        )

    def save_pinned_items(item):
        pinned_items = []
        for item in tray.items:
            if item.app is not None and item.is_pinned:
                pinned_items.append(item.app.path)
        with open(get_pinned_items_path(), "w") as f:
            json.dump(pinned_items, f)

    def window_opened(screen, window):
        for item in tray.items:
            if item.offer_window(window):
                return
        appitem = AppItem(
            win_config, appitem_config, screen, window.get_class_group()
        )
        appitem.connect("pinned", save_pinned_items)
        appitem.connect("unpinned", save_pinned_items)
        appitem.add_window(window)
        tray.add_item(None, appitem)

    screen_handlers = [
        screen.connect("window-opened", window_opened),
    ]

    def manage():
        pinned_items_path = get_pinned_items_path()
        if os.path.exists(pinned_items_path):
            with open(pinned_items_path, "r") as f:
                pinned_items = json.load(f)
            for path in pinned_items:
                yield None
                try:
                    app = ROXApp(path)
                except AppError:
                    try:
                        app = DesktopApp(path)
                    except AppError:
                        continue
                appitem = AppItem(
                    win_config,
                    appitem_config,
                    screen,
                    class_group=None,
                    app=app,
                    pinned=True,
                )
                tray.add_item(None, appitem)
        class_group2windows = {}
        for window in screen.get_windows():
            window_opened(screen, window)
            yield None
        state.initializing = False

    def unmanage():
        yield None

    def item_added(tray, item):
        if not state.initializing:
            save_pinned_items(item)
        item.connect("pinned", save_pinned_items)
        item.connect("unpinned", save_pinned_items)

    tray.connect("item-added", item_added)

    return manage, unmanage
