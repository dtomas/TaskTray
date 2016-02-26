import os

import rox
from rox import AppInfo, processes, filer

from traylib import APPDIRPATH

from tasktray.app import AppError, AppAction


class ROXApp(object):

    def __init__(self, app_dir):
        if not rox.isappdir(app_dir):
            raise AppError("No an app dir: %s" % app_dir)
        self.__path = app_dir
        help_dir = os.path.join(app_dir, 'Help')
        if os.path.isdir(help_dir):
            self.__help_dir = help_dir
        self.__name = os.path.basename(app_dir)
        self.__app_run = os.path.join(app_dir, 'AppRun')
        app_info = os.path.join(app_dir, 'AppInfo.xml')
        if os.access(app_info, os.R_OK):
            self.__app_options = [
                AppAction(
                    option.get('label'),
                    [self.__app_run, option.get('option')],
                    option.get('icon')
                )
                for option in AppInfo.AppInfo(app_info).getAppMenu()
            ]
        else:
            self.__app_options = []

    @property
    def help_dir(self):
        return self.__help_dir

    @property
    def path(self):
        return self.__path

    @property
    def name(self):
        return self.__name

    @property
    def id(self):
        return self.__name

    @property
    def options(self):
        return self.__app_options

    icon_name = None

    def run(self):
        processes.PipeThroughCommand([self.__app_run], None, None).start()

    @staticmethod
    def from_name(appname):
        for path in APPDIRPATH:
            if not path:
                continue
            app_dir = os.path.join(path, appname)
            if not os.path.isdir(app_dir):
                app_dir = os.path.join(path, appname.capitalize())
            if not os.path.isdir(app_dir):
                app_dir = os.path.join(path, appname.upper())
            try:
                return ROXApp(app_dir)
            except AppError:
                continue
        return None
