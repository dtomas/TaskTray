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

    def class_group_opened(screen, class_group):
        for item in tray.items:
            if item.offer_class_group(class_group):
                return
        appitem = AppItem(win_config, appitem_config, screen, class_group)
        appitem.connect("pinned", save_pinned_items)
        appitem.connect("unpinned", save_pinned_items)
        tray.add_item(None, class_group.get_name(), appitem)

    screen_handlers = [
        screen.connect("class-group-opened", class_group_opened),
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
                appitem.connect("pinned", save_pinned_items)
                appitem.connect("unpinned", save_pinned_items)
                tray.add_item(None, app.id, appitem)
        class_group2windows = {}
        for window in screen.get_windows():
            class_group = window.get_class_group()
            if class_group in class_group2windows:
                class_group2windows[class_group].append(window)
            else:
                class_group2windows[class_group] = [window]
        for class_group in class_group2windows:
            class_group_opened(screen, class_group)
            yield None

    def unmanage():
        yield None

    return manage, unmanage
