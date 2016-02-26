import os
import subprocess
from ConfigParser import RawConfigParser, NoOptionError

from rox.basedir import xdg_data_dirs

from traylib.icons import ThemedIcon, FileIcon

from tasktray.app import AppError, AppAction


class DesktopApp(object):

    def __init__(self, desktop_file):
        if not os.path.exists(desktop_file):
            raise AppError("Desktop file %s does not exist." % desktop_file)
        parser = RawConfigParser()
        parser.read(desktop_file)
        try:
            self.__exec = parser.get("Desktop Entry", "Exec")
        except NoOptionError:
            raise AppError("No Exec entry in .desktop file %s." % desktop_file)
        self.__id = os.path.splitext(os.path.basename(desktop_file))[0]
        try:
            self.__name = parser.get("Desktop Entry", "Name")
        except NoOptionError:
            self.__name = self.__id
        try:
            self.__icon_name = parser.get("Desktop Entry", "Icon")
        except NoOptionError:
            self.__icon_name = None
        self.__app_options = []
        for section in parser.sections():
            if not section.startswith("Desktop Action"):
                continue
            self.__app_options.append({
                "label": parser.get(section, "Name"),
                "exec": parser.get(section, "Exec"),
            })
        self.__path = desktop_file
        self.__help_dir = None
        for datadir in xdg_data_dirs:
            help_dir = os.path.join(datadir, 'doc', self.__id)
            if os.path.isdir(help_dir):
                self.__help_dir = help_dir
                break
        self.__app_options = []
        for section in parser.sections():
            if not section.startswith("Desktop Action"):
                continue
            try:
                name = parser.get(section, "Name")
            except NoOptionError:
                continue
            try:
                exec_ = parser.get(section, "Exec")
            except NoOptionError:
                continue
            try:
                icon_name = parser.get(section, "Icon")
            except NoOptionError:
                icon_name = None
            self.__app_options.append(
                AppAction(name, exec_.split(' '), icon_name)
            )

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
        return self.__id

    @property
    def options(self):
        return self.__app_options

    @property
    def icons(self):
        if os.path.isabs(self.__icon_name):
            return [FileIcon(self.__icon_name)]
        else:
            return [ThemedIcon(self.__icon_name)]

    def run(self):
        command = [
            arg for arg in self.__exec.split(' ')
            if arg not in {"%f", "%F", "%u", "%U"}
        ]
        subprocess.Popen(command)

    @staticmethod
    def from_name(appname):
        for datadir in xdg_data_dirs:
            applications_dir = os.path.join(datadir, "applications")
            for leafname in appname, appname.lower(), appname.capitalize():
                desktop_file = os.path.join(
                    applications_dir, leafname + ".desktop"
                )
                try:
                    return DesktopApp(desktop_file)
                except AppError:
                    continue
        return None
