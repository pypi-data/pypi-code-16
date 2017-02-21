from cloudshell.shell.core.driver_context import AutoLoadAttribute


class AttributeContainer(list):
    _DEFAULT_VALUE = ''
    _DEFAULT_VALUES = {}

    def __init__(self, relative_path=None, **attributes_dict):
        self._default_values = {}
        self.handle_attributes_dict(relative_path, attributes_dict)

    def append_attribute(self, relative_path, attribute_name, attribute_param):
        if callable(attribute_param):
            attribute_value = attribute_param()
        else:
            attribute_value = attribute_param

        attribute = AutoLoadAttribute(relative_path, attribute_name, attribute_value)
        self.append(attribute)

    def get_attributes_list(self):
        return [getattr(self, attr) for attr in dir(self) if attr.isupper() and not attr.startswith('_')]

    def handle_attributes_dict(self, relative_path, attr_dict):
        for attr in self.get_attributes_list():
            if attr in attr_dict and attr_dict[attr]:
                attr_value = attr_dict[attr]
            elif attr in self._DEFAULT_VALUES:
                attr_value = self._DEFAULT_VALUES[attr]
            else:
                attr_value = self._DEFAULT_VALUE
            self.append_attribute(relative_path, attr, attr_value)
