from pyalsi.colors import bold, normal


class Colors(object):
    colors = {"low": bold["green"],
              "med": bold["yellow"],
              "high": bold["red"],
              "red": normal["red"]
              }

    def set(self, k, v):
        self.colors[k] = v


def colorize(heading, value):
    """
    wrapper to colorize info lines
    :param heading: line heading (eg. "OS")
    :param value: line value (eg. "Arch Linux")
    :return: string (eg. "{c2}OS: {c1}Arch Linux")
    """
    return "{c2}" + heading + ": {c1}" + str(value)


def colorize_usage(use, total, percent, unit):
    """
    colorizes the passed string based on the percentage passed in
    :param use: output variable
    :param total: output variable
    :param percent: used to calculate the appropriate color
    :param unit: essentially a suffix to use and total (eg. "G | M")
    :return: string (eg. "{low}43G{c1} / 87G")
    """
    level = '{low}' if percent <= 50 else '{med}' if percent < 80 else '{high}'
    return level + str(use) + unit + "{c1} / " + str(total) + unit


def colorize_percent(value, suffix=""):
    """
    as above but only takes one output variable
    :param value: the output variable
    :param suffix: string to put after value (eg. "%)
    :return: string (eg. "{low}15%{c1}")
    """
    level = '{low}' if value <= 50 else '{med}' if value < 80 else '{high}'
    return level + str(value) + suffix + "{c1}"
