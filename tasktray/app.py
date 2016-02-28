import re
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
