import collections
import re

from selenium.common.exceptions import NoSuchElementException

from sulfur import errors


class QueriableMixin:
    """
    Mixin that defines the .get() and .find() methods for subclasses.
    """

    _query_tests = collections.OrderedDict()

    def elem(self, selector, raises=True, unique=False):
        """
        Returns the first element that satisfy the given selector.
        """

        if unique:
            qs = self.find(selector, allow_empty=False)
            if len(qs) == 1:
                return qs[0]
            msg = 'query %r returned %s elements' % (selector, len(qs))
            raise errors.MultipleElementsFoundError(msg)
        try:
            wrapper = self._wrap_element
            return self.__worker('find_element_by_', wrapper, selector)
        except NoSuchElementException:
            if raises:
                raise errors.NotFoundError('no element %r found' % selector)

    def find(self, selector, allow_empty=True):
        """
        QuerySet current page for the CSS selector pattern.

        Args:
            selector (str):
                A css or xpath selector.
            allow_empty (bool):
                If False, raise a NotFoundError if resulting queryset is empty.
        """

        wrapper = self._wrap_queryset
        return self.__worker('find_elements_by_', wrapper, selector)

    def _get_selenium_queryset_object(self):
        raise NotImplementedError('must be implemented in subclasses')

    def _wrap_element(self, element):
        raise NotImplementedError('must be implemented in subclasses')

    def _wrap_queryset(self, selector):
        raise NotImplementedError('must be implemented in subclasses')

    def _get_query_method_suffix(self, selector):
        for func, name in self._query_tests.items():
            if func(selector):
                return name
        return 'css_selector'

    def __worker(self, base, wrapper, selector):
        delegate = self._get_selenium_queryset_object()
        query_type = self._get_query_method_suffix(selector)
        method = getattr(delegate, base + query_type)
        return wrapper(method(selector))


#
# Utility functions
#
TAG_SELECTOR_REGEX = re.compile(r'^(\w|-)+$')
ID_SELECTOR_REGEX = re.compile(r'^\#(\w|-)+$')
CLASS_SELECTOR_REGEX = re.compile(r'^\.(\w|-)+$')


def is_id_selector(selector):
    """
    Return True if CSS selector is of the form #id-name.
    """

    return ID_SELECTOR_REGEX.match(selector) is not None


def is_class_selector(selector):
    """
    Return True if CSS selector is of the form #id-name.
    """

    return CLASS_SELECTOR_REGEX.match(selector) is not None


def is_tag_selector(selector):
    """
    Return True if CSS selector is of the form #id-name.
    """

    return TAG_SELECTOR_REGEX.match(selector) is not None


def is_xpath_selector(selector):
    """
    Return True if selector defines an xpath.
    """

    # TODO: Fixme
    return False


def is_link_selector(selector):
    """
    Return True if receives a link selector.
    """

    # TODO: Fixme
    return False


def is_partial_link_selector(selector):
    """
    Return True if receives a partial link selector.
    """

    # TODO: Fixme
    return False


def is_name_selector(selector):
    """
    Return True if receives a name selector.
    """

    # TODO: Fixme
    return False


QueriableMixin._query_tests.update([
    (is_id_selector, 'id'),
    (is_class_selector, 'class_name'),
    (is_tag_selector, 'tag_name'),
    (is_partial_link_selector, 'partial_link_name'),
    (is_link_selector, 'link_name'),
    (is_xpath_selector, 'xpath'),
    (is_name_selector, 'name'),
])
