import os
from gi.repository import Gio

from rox.basedir import xdg_data_dirs

from traylib.icons import GioIcon

from tasktray.app import IApp, normalize_app_id


class DesktopAppAction(object):

    def __init__(self, appinfo, action_name):
        self.action_name = action_name
        self.label = appinfo.get_action_name(action_name)

    def execute(self):
        self.appinfo.launch_action(self.action, None)


class DesktopApp(IApp):

    def __init__(self, appinfo):
        self.appinfo = appinfo
        self.__help_dir = None
        for datadir in xdg_data_dirs:
            help_dir = os.path.join(datadir, 'doc', self.id)
            if os.path.isdir(help_dir):
                self.__help_dir = help_dir
                break
        self.__app_actions = [
            DesktopAppAction(appinfo, action_name)
            for action_name in self.appinfo.list_actions()
        ]

    @property
    def description(self):
        return self.appinfo.get_description()

    @property
    def help_dir(self):
        return self.__help_dir

    @property
    def path(self):
        return self.appinfo.get_property("filename")

    @property
    def name(self):
        return self.appinfo.get_name()

    @property
    def id(self):
        app_id = self.appinfo.get_id()
        if app_id.endswith('.desktop'):
            app_id = app_id[:-len('.desktop')]
        return app_id

    @property
    def actions(self):
        return self.__app_actions

    @property
    def icons(self):
        icon = self.appinfo.get_icon()
        return [] if icon is None else [GioIcon(icon)]

    @property
    def is_drop_target(self):
        return (
            self.appinfo.supports_files()
            or self.appinfo.supports_uris()
        )

    @property
    def command(self):
        return None

    def run(self, uri_list=None):
        self.appinfo.launch_uris(uri_list)

    @classmethod
    def from_path(cls, path):
        try:
            appinfo = Gio.DesktopAppInfo.new_from_filename(path)
        except TypeError:
            # XXX: Constructor returned NULL.
            return None
        if appinfo is None:
            return None
        return cls(appinfo)

    @classmethod
    def from_name(cls, appname):
        desktop_id = normalize_app_id(appname) + '.desktop'
        try:
            appinfo = Gio.DesktopAppInfo.new(desktop_id)
        except TypeError:
            # XXX: Constructor returned NULL.
            return None
        if appinfo is None:
            return None
        return cls(appinfo)
