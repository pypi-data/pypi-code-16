CMD_LINE_TABLE = dict()


def cmdline(module, shell_code):
    def generator(func):
        CMD_LINE_TABLE[func.__name__] = shell_code
        return func
    return generator
