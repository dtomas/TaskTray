import subprocess


class AppAction(object):

    def __init__(self, label, command, stock_icon):
        self.label = label
        self.command = command
        self.stock_icon = stock_icon

    def execute(self):
        subprocess.Popen(self.command)
        

class AppError(Exception):
    pass
