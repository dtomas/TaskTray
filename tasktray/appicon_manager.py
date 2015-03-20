from tasktray.appicon import AppIcon


def manage_appicons(tray, screen, icon_config, win_config, appicon_config):

    class_groups = {}

    tray.add_box(None)

    def window_opened(screen, window):
        class_group = window.get_class_group()
        icon = tray.get_icon(class_group)
        if not icon:
            icon = AppIcon(icon_config, win_config, appicon_config,
                           class_group, screen)
            icon.update_name()
            icon.update_icon()
            tray.add_icon(None, class_group, icon)
        class_groups[window] = class_group

    def window_closed(screen, window):
        class_group = class_groups.get(window)
        if not class_group:
            return
        icon = tray.get_icon(class_group)
        if icon:
            if not icon.has_windows:
                tray.remove_icon(class_group)
            else:
                icon.update_icon()
        del class_groups[window]

    window_opened_handler = screen.connect("window-opened", window_opened)
    window_closed_handler = screen.connect("window-closed", window_closed)

    def manage():
        for window in screen.get_windows():
            window_opened(screen, window)
            yield None

    def unmanage():
        screen.disconnect(window_opened_handler)
        screen.disconnect(window_closed_handler)
        yield None

    return manage, unmanage