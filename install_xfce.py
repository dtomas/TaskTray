import sys
import os


sys.path.append(os.path.join(os.path.dirname(__file__), 'TrayLib'))
sys.path.append(
    os.path.join(os.path.dirname(__file__), 'rox-lib', 'ROX-Lib2', 'python')
)

from traylib.xfce import install_panel_plugin


install_panel_plugin('TaskTray', 'tasktray_xfce.sh')
