from lxml import etree


import logging
log = logging.getLogger("XMLTestLogger")


class Operator:

    @classmethod
    def check(self, condition, input_value, expected_value):
        if condition == 'eq':
            return input_value == expected_value
        if condition == 'ne':
            return input_value != expected_value


class Comparator:

    def compare(self):
        raise NotImplementedError("Comparator should implement compare() \
                                  method")

    @classmethod
    def new_comparator(self, nick, property, init_property):
        if nick == 'xpath':
            return XMLComparator(property, init_property)


class XMLComparator(Comparator):

    def __init__(self, xpath_value, init_property):
        self.nick = 'xpath'
        if 'xpath' not in init_property:
            raise Exception("xpath is required field for XMLComparator")
        self.xpath = init_property['xpath']

        if 'comparator' not in init_property:
            raise Exception("comparator is required field in XMLComparator, \
                            specifies the condition to use for matching")
        self.condition = init_property['comparator']

        if 'type' not in init_property:
            raise Exception("type describes the type of data to be extracted.\
                            can be tag/text. It is required field for XML Comparators")
        self._type = init_property['type']

        if 'expected' not in init_property:
            raise Exception("expected is a required field in XMLComparator, \
                            required to perform a match with the extracted data")
        self.expected_value = init_property['expected']

        log.debug("     XMLCOMPARATOR:" + self.__to_string__())

    def to_string(self):
        return (self.nick + " " + str(self.xpath) + " " + str(self.condition) +
                " " + str(self._type))

    def __to_string__(self):
        return "\n        NICK: " + str(self.nick) \
            + "\n        XPATH: " + str(self.xpath) \
            + "\n        CONDITION: " + str(self.condition) \
            + "\n        TYPE: " + str(self._type)

    def compare(self, response_content):
        # Evaluate XPATH on xml_content
        try:
            input_value = None
            tree = etree.fromstring(response_content)
            # Hardcoding for now, will pick only the first element
            elements = tree.xpath(self.xpath)
            element = None

            if len(elements) > 0:
                element = elements[0]
            else:
                raise Exception("XPath don't match any element")

            # Evaluate based on type
            if self._type == 'tag':
                input_value = element.tag

            if self._type == 'text':
                input_value = element.text

            if self._type == 'element':
                input_value = element

            if self._type == 'length':
                input_value = len(element)

            log.debug("\n\nComparator:  " + self.to_string())
            log.debug("-- Value From Content:")
            log.debug(input_value)
            log.debug("-- Expected Value: ")
            log.debug(self.expected_value)

            return Operator.check(self.condition, input_value,
                                  self.expected_value)
        except BaseException as ex:
            log.error(ex.message)
            raise Exception("Comparator Error: " + ex.message)
