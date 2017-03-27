params = {}
temp_params = {}


def Params(paramName, options):
    params[paramName] = options

    def aaa():
        if paramName in temp_params:
            return temp_params[paramName]
        else:
            return params[paramName]['default']
    return aaa


def getAllParams():
    return params