import re
import abc
import subprocess


def normalize_app_id(app_id):
    return re.sub("[0-9\.\-]", "", app_id.lower())


class AppAction(object):

    def __init__(self, label, command, stock_icon):
        self.label = label
        self.command = command
        self.stock_icon = stock_icon

    def execute(self):
        subprocess.Popen(self.command)
        

class AppError(Exception):
    pass


class IApp(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def description(self):
        """A one-line description of the app, localized if possible."""

    @abc.abstractproperty
    def id(self):
        """The app's identifier."""

    @abc.abstractproperty
    def name(self):
        """The app's name, localized if possible."""

    @abc.abstractproperty
    def path(self):
        """The path of the app file or dir."""

    @abc.abstractproperty
    def actions(self):
        """List of L{AppAction}s."""

    @abc.abstractproperty
    def help_dir(self):
        """The help directory path."""

    @abc.abstractproperty
    def icons(self):
        """List of L{IIconLoader}s."""

    @abc.abstractproperty
    def is_drop_target(self):
        """C{True} if URIs can be dropped on the app."""

    @abc.abstractproperty
    def run(self, uri_list=()):
        """Runs the app with the given URIs."""

    @abc.abstractproperty
    def command(self):
        """The executable path."""
