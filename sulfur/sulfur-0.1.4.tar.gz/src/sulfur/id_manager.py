class IdManager:
    """
    IdManager corresponds to the Driver.id attribute which exposes an interface
    to obtain elements from the id.
    """

    def __init__(self, driver):
        self.__dict__['_IdManager__driver'] = driver

    def __getattr__(self, id):
        return self[id]

    def __setattr__(self, id, value):
        self[id] = value

    def __getitem__(self, id):
        return self.__driver.find_element_by_id(id)

    def __setitem__(self, id, value):
        self[id].send_keys(value)