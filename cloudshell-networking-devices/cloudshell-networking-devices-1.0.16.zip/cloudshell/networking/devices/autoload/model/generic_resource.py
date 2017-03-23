from cloudshell.shell.core.driver_context import AutoLoadResource
from cloudshell.networking.devices.autoload.model.attribute_container import AttributeContainer


class GenericResource(AutoLoadResource):
    ATTRIBUTE_CONTAINER = AttributeContainer
    MODEL = 'Generic Resource'
    NAME_TEMPLATE = 'Resource{0}'
    RELATIVE_PATH_TEMPLATE = '{0}/{1}'
    ID_TEMPLATE_WITH_CONTAINER_ID = '{0}{1}'
    NEED_VALIDATION = True

    def __init__(self, element_id, name=None, container_id=None, model=None, relative_path=None, unique_id=None,
                 **attributes_dict):
        """
        Generic resource

        :param element_id: Can be any positive number or -1. If specified -1, id will be taken from the end
        of the sequence
        :param container_id:
        :param name:
        :param model:
        :param relative_path:
        :param unique_id:
        :param attributes_dict:
        :return:
        """
        if element_id is None or element_id is '':
            self.element_id = -1
        else:
            self.element_id = int(element_id)


        self._container_id = container_id

        if not name and element_id >= 0 and self.NAME_TEMPLATE:
            self.name = self.NAME_TEMPLATE.format(self._generate_element_id_string())
        else:
            self.name = name

        self.model = model or self.MODEL
        self.relative_address = relative_path
        self.unique_identifier = unique_id

        if attributes_dict:
            self._attributes = self.ATTRIBUTE_CONTAINER(relative_path, **attributes_dict)
        else:
            self._attributes = []

    def _generate_element_id_string(self):
        if self._container_id:
            id_string = self.ID_TEMPLATE_WITH_CONTAINER_ID.format(self._container_id, self.element_id)
        else:
            id_string = str(self.element_id)
        return id_string

    def build_attributes(self, attributes_dict):
        self._attributes = self.ATTRIBUTE_CONTAINER(self.relative_address, **attributes_dict)

    def build_relative_path(self, parent_path):
        if not self.name and self.NAME_TEMPLATE:
            self.name = self.NAME_TEMPLATE.format(self._generate_element_id_string())

        if self.RELATIVE_PATH_TEMPLATE is None:
            self.relative_address = ''
        elif parent_path:
            self.relative_address = self.RELATIVE_PATH_TEMPLATE.format(parent_path, self._generate_element_id_string()
)
        else:
            self.relative_address = self.RELATIVE_PATH_TEMPLATE.format(self._generate_element_id_string())

        self._set_relative_path_to_attributes()

    def _build_relative_path_for_child_resources(self, *child_resources):
        if len(child_resources) > 0:
            for resource in reduce(lambda x, y: x + y, child_resources):
                resource.build_relative_path(self.relative_address)

    def _set_relative_path_to_attributes(self):
        for attribute in self._attributes:
            attribute.relative_address = self.relative_address

    def get_attributes(self):
        return self._attributes

    @staticmethod
    def _get_attributes_for_child_resources(*child_resources):
        attributes = []
        if len(child_resources) > 0:
            for resource in reduce(lambda x, y: x + y, child_resources):
                attributes += resource.get_attributes()
        return attributes

    def get_resources(self):
        return [self]

    @staticmethod
    def _get_resources_for_child_resources(*child_resources):
        resources = []
        if len(child_resources) > 0:
            for resource in reduce(lambda x, y: x + y, child_resources):
                resources += resource.get_resources()
            return resources

    @staticmethod
    def _validate_child_ids(*child_resources):
        elements_ids = []
        zero_elements = []
        for element in reduce(lambda x, y: x + y, child_resources):
            if element.NEED_VALIDATION:
                if int(element.element_id) == -1 or int(element.element_id) in elements_ids:
                    zero_elements.append(element)
                else:
                    elements_ids.append(int(element.element_id))

        for element in zero_elements:
            if len(elements_ids) > 0:
                element.element_id = max(elements_ids) + 1
            else:
                element.element_id = 0
            elements_ids.append(element.element_id)
