from traylib.config import Config, Attribute


class AppIconConfig(Config):
    themed_icons = Attribute(default=False)
    """
    C{True} if TaskTray should try to use icons from themes for L{AppIcon}s.
    """
