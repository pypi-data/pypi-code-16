class GenericError(Exception):
    """Basic Exception for modules"""
    def __init__(self, func, msg=None):
        if msg is None:
            print("An error occurred on the function: " + func)
        super(GenericError, self).__init__(msg)
        self.func = func


class NoRecordsFoundError(Exception):
    """No Record Found while parsing"""
    def __init__(self, location, msg=None):
        if msg is None:
            print("No Records Found: no records found while parsing: " + location)
        super(NoRecordsFoundError, self).__init__(msg)
        self.location = location


class ProductChooserError(Exception):
    """Called when there is an issue using Product Chooser"""
    def __init__(self, problem, msg=None):
        if msg is None:
            print("An error occurred with the product chooser: " + problem)
        super(ProductChooserError, self).__init__(msg)
        self.problem = problem


class ProductChooserAddError(Exception):
    """Called when there is an issue using Product Chooser"""
    def __init__(self, problem, msg=None):
        if msg is None:
            print("An error occurred with the product chooser" + problem)
        super(ProductChooserAddError, self).__init__(msg)
        self.problem = problem


class LogicError(Exception):
    """Basic exception for Logic Module"""
    def __init__(self, func, msg=None):
        if msg is None:
            print("An error occurred on the function: " + func)
        super(LogicError, self).__init__(msg)
        self.func = func


class DataRetreivalError(Exception):
    """Basic exception for Logic Module when data cannot be properly pulled and or read from a dict"""
    def __init__(self, func, msg=None):
        if msg is None:
            print("Could not read data from dict.")
        super(DataRetreivalError, self).__init__(msg)
        self.func = func


class DataLibError(Exception):
    """Basic exception for when data was either not retrieved from or could not be found in the ci_data_library.json file"""
    def __init__(self, item=None, msg=None):
        if item is None:
            print("Could not find item in the current data set. Please rebuild the data library.")
        elif item is not None:
            if msg is None:
                print("Could not find [{}] in the current data set. Please rebuild the data library.". format(item))
            if msg is not None:
                print("Could not find [{}] in the current data set. {}".format(item, msg))
        super(DataLibError, self).__init__(item, msg)
        self.item = item


class InvalidItemError(Exception):
    """Called when item cannot be found in data set"""
    def __init__(self, item, msg=None):
        if msg is None:
            print(item + " > Cannot be found in the supplied data set. Item may not be spelled correctly, data is corrupt, or item does not exist")
        super(InvalidItemError, self).__init__(msg)
        self.item = item


class SelectionError(Exception):
    """Basic Selection Exception for modules"""
    def __init__(self, func, element, msg=None):
        if msg is None:
            print("Unable to interact with element:  " + element + " : " + func)
        super(SelectionError, self).__init__(msg)
        self.func = func
        self.element = element


class MissingInformationError(Exception):
    """Called when information is missing from ini file"""
    def __init__(self, section, key_list, msg=None):
        if msg is None:
            print("Required information is missing. Section [{}] Keys: {}".format(section.upper(), str(key_list)))
        if msg is not None:
            print(msg + " Section [{}]: Keys: {}".format(section.upper(), str(key_list)))
            input('Press any key to continue...')
        super(MissingInformationError, self).__init__(msg)
        self.section = section
        self.key_list = key_list


class WaitTimeOutError(Exception):
    """Called when time overflows"""
    def __init__(self, n, selector, msg=None):
        if msg is None:
            print("Function timed out after [" + n + "] iterations on selector [" + selector + "]")
        super(WaitTimeOutError, self).__init__(msg)
        self.n = n
        self.selector = selector


class NetworkDriveError(Exception):
    '''Called when there is an issue with the mapped network drive'''
    def __init__(self, resolution, issue='NetworkDriveError', msg=None):
        if msg is None:
            print(issue + ': An issue occurred when connecting to the network drive. ' + resolution)
        else:
            print(issue + ': An issue occurred when connecting to the network drive. ' + resolution)
        super(NetworkDriveError, self).__init__(msg)
        self.resolution = resolution


class NetworkError(Exception):
    '''Called when there is an issue with the vpn / server connection'''
    def __init__(self, resolution, issue='NetworkConnectionError', msg=None):
        if msg is None:
            print(issue + ': Unable to connect to the server. ' + resolution)
        else:
            print(issue + ': ' + msg + '. ' + resolution)
        super(NetworkDriveError, self).__init__(msg)
        self.resolution = resolution