import os
import locale
import subprocess
from ConfigParser import RawConfigParser, NoOptionError, Error

from rox import get_local_path
from rox.basedir import xdg_data_dirs

from traylib.icons import ThemedIcon, FileIcon

from tasktray.app import AppError, AppAction, normalize_app_id


class DesktopApp(object):

    def __init__(self, desktop_file):
        if not os.path.exists(desktop_file):
            raise AppError("Desktop file %s does not exist." % desktop_file)
        parser = RawConfigParser()
        try:
            parser.read(desktop_file)
        except Error as e:
            raise AppError("Error reading file %s: %s" % (desktop_file, e))
        if not parser.has_section("Desktop Entry"):
            raise AppError("No desktop entry section in %s." % desktop_file)
        lang = locale.getdefaultlocale()[0].split('_')[0]
        try:
            self.__exec = parser.get("Desktop Entry", "Exec")
        except NoOptionError:
            raise AppError("No Exec entry in .desktop file %s." % desktop_file)
        self.__id = os.path.splitext(os.path.basename(desktop_file))[0]
        self.__name = self.__id
        try:
            self.__name = parser.get("Desktop Entry", "Name[%s]" % lang)
        except NoOptionError:
            try:
                self.__name = parser.get("Desktop Entry", "Name")
            except NoOptionError:
                pass
        try:
            self.__icon_name = parser.get("Desktop Entry", "Icon")
        except NoOptionError:
            self.__icon_name = None
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
                name = parser.get(section, "Name[%s]" % lang)
            except NoOptionError:
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
        self.__is_drop_target = (
            "%f" in self.__exec or
            "%F" in self.__exec or
            "%u" in self.__exec or
            "%U" in self.__exec
        )
        self.__is_multi_drop = "%F" in self.__exec or "%U" in self.__exec
        try:
            self.__description = parser.get("Desktop Entry", "Comment")
        except NoOptionError:
            self.__description = self.__name

    @property
    def description(self):
        return self.__description

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

    @property
    def is_drop_target(self):
        return self.__is_drop_target

    @property
    def command(self):
        return self.__exec

    def run(self, uri_list=[]):
        if not self.__is_drop_target:
            subprocess.Popen(self.__exec.split(' '))
        else:
            if self.__is_multi_drop:
                command = []
                for arg in self.__exec.split(' '):
                    if arg == "%U":
                        for uri in uri_list:
                            command.append(uri)
                    elif arg == "%F":
                        for uri in uri_list:
                            command.append(get_local_path(uri))
                    else:
                        command.append(arg)
                subprocess.Popen(command)
            else:
                if not uri_list:
                    subprocess.Popen([
                        arg for arg in self.__exec.split(' ')
                        if arg not in {"%u", "%f"}
                    ])
                else:
                    for uri in uri_list:
                        command = []
                        for arg in self.__exec.split(' '):
                            if arg == "%u":
                                command.append(uri)
                            elif arg == "%f":
                                command.append(get_local_path(uri))
                            else:
                                command.append(arg)
                        subprocess.Popen(command)

    @staticmethod
    def from_name(appname):
        appname = normalize_app_id(appname)
        for datadir in xdg_data_dirs:
            applications_dir = os.path.join(datadir, "applications")
            if not os.path.isdir(applications_dir):
                continue
            filenames = os.listdir(applications_dir)
            for leafname in filenames:
                if (normalize_app_id(os.path.splitext(leafname)[0].lower()) ==
                        appname):
                    return DesktopApp(os.path.join(applications_dir, leafname))
        return None
