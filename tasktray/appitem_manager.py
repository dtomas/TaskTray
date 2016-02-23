from tasktray.appitem import AppItem

from traylib.icon_renderer import render_icon


def manage_appitems(tray, screen, icon_config, win_config, appitem_config):

    tray.add_box(None)

    def class_group_opened(screen, class_group):
        tray.add_item(
            None, class_group,
            AppItem(win_config, appitem_config, class_group, screen)
        )

    screen_handlers = [
        screen.connect("class-group-opened", class_group_opened),
    ]

    def manage():
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
