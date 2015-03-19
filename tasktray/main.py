import rox
from rox.options import Option

from traylib.main import Main
from traylib.winicon import WinIconConfig

from tasktray import TaskTray
from tasktray.appicon_config import AppIconConfig

import wnck


class TaskTrayMain(Main):
    
    def __init__(self):
        Main.__init__(self, "TaskTray")
        try:
            wnck.set_client_type(wnck.CLIENT_TYPE_PAGER)
        except:
            pass

    def init_options(self):
        Main.init_options(self)
        self.__o_all_workspaces = Option("all_workspaces", False)
        self.__o_arrow = Option("arrow", True)
        self.__o_themed_icons = Option("themed_icons", False)
        
    def init_config(self):
        Main.init_config(self)
        self.__win_config = WinIconConfig(
            all_workspaces=self.__o_all_workspaces.int_value, 
            arrow=self.__o_arrow.int_value,
        )

        self.__appicon_config = AppIconConfig(
            themed_icons=self.__o_themed_icons.int_value,
        )

        # TaskTray doesn't use the 'hidden' option, so make sure no icons get
        # hidden.
        self.icon_config.hidden = False
        
    def mainloop(self, app_args):
        Main.mainloop(self, 
                      app_args, 
                      TaskTray, 
                      self.__win_config, 
                      self.__appicon_config)

    def options_changed(self):
        if self.__o_arrow.has_changed:
            self.__win_config.arrow = self.__o_arrow.int_value
    
        if self.__o_all_workspaces.has_changed:
            self.__win_config.all_workspaces = self.__o_all_workspaces.int_value
            
        if self.__o_themed_icons.has_changed:
            self.__appicon_config.themed_icons = self.__o_themed_icons.int_value

        Main.options_changed(self)

    win_config = property(lambda self : self.__win_config)
    appicon_config = property(lambda self : self.__appicon_config)
