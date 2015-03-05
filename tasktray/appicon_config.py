from traylib.config import Config


class AppIconConfig(Config):
    
    def __init__(self, themed_icons):
        """
        Creates a new C{AppIconConfig}.
        
        @param themed_icons: C{True} if the AppIcons' icons should be looked up
            from the current icon theme.
        """
        Config.__init__(self)
        self.add_attribute('themed_icons', themed_icons,
                           'update_option_themed_icons')
    
    themed_icons = property(lambda self : self.get_attribute('themed_icons'),
            lambda self, themed_icons : self.set_attribute('themed_icons',
                                                           themed_icons))
