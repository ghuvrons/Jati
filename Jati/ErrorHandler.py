class HTTPError(RuntimeError):
    def __init__(self, *arg):
        if not type(arg) is tuple:
            arg = (arg, "Server error",)
        if len(arg) == 0:
            arg = (500, "Server error",)
        elif len(arg) == 1:
            arg = arg + ("Server error",)
        self.args = arg

class WSError(RuntimeError):
    def __init__(self, *arg):
        if not type(arg) is tuple:
            arg = (arg, "Server error",)
        if len(arg) == 0:
            arg = (500, "Server error",)
        elif len(arg) == 1:
            arg = arg + ("Server error",)
        self.args = arg

class JatiError(RuntimeError):
    def __init__(self, *arg):
        self.args = arg