import os
import subprocess

import rox
from rox import AppInfo, filer

from traylib import APPDIRPATH
from traylib.icons import FileIcon

from tasktray.app import AppError, AppAction


class ROXApp(object):

    def __init__(self, app_dir):
        if not rox.isappdir(app_dir):
            raise AppError("Not an app dir: %s" % app_dir)
        self.__path = app_dir
        help_dir = os.path.join(app_dir, 'Help')
        if os.path.isdir(help_dir):
            self.__help_dir = help_dir
        self.__name = os.path.basename(app_dir)
        self.__app_run = os.path.join(app_dir, 'AppRun')
        self.__dir_icon = os.path.join(app_dir, '.DirIcon')
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

    @property
    def icons(self):
        return [FileIcon(self.__dir_icon)]

    is_drop_target = True

    def run(self, uri_list=[]):
        subprocess.Popen([self.__app_run] + list(uri_list))

    @staticmethod
    def from_name(appname):
        appnames = [appname, appname.capitalize(), appname.upper()]
        for path in APPDIRPATH:
            if not path or not os.path.isdir(path):
                continue
            for filename in os.listdir(path):
                if filename.lower() == appname.lower():
                    app_dir = os.path.join(path, filename)
                    try:
                        return ROXApp(app_dir)
                    except AppError:
                        pass
        return None
