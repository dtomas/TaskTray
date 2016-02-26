from rox import processes


class AppAction(object):

    def __init__(self, label, command, stock_icon):
        self.label = label
        self.command = command
        self.stock_icon = stock_icon

    def execute(self):
        processes.PipeThroughCommand(self.command, None, None).start()
        

class AppError(Exception):
    pass
