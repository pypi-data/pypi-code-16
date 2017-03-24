from collections import Sequence

from sulfur.queriable import QueriableMixin


class QuerySet(Sequence, QueriableMixin):
    """
    A query set of elements in a page.

    Queries can be filtered and iterated. Most query methods can be chained
    as in the example:

    >>> q = ...  # driver method that return a query set object
    >>> q.filter('div').click()                                  # pytest: +SKIP
    """

    @property
    def is_visible(self):
        return all(x.is_visible for x in self)

    @property
    def is_enabled(self):
        return all(x.is_enabled for x in self)

    @property
    def is_selected(self):
        return all(x.is_selected for x in self)

    def __init__(self, elements, parent):
        self.parent = parent
        self.elements = list(elements or [])

    def __repr__(self):
        data = ', '.join(repr(x) for x in self)
        return '<QuerySet: [%s]>' % data

    def __iter__(self):
        return iter(self.elements)

    def __len__(self):
        return len(self.elements)

    def __getitem__(self, i):
        return self.elements[i]

    def __eq__(self, other):
        if isinstance(other, Sequence):
            if len(self) == len(other):
                if all(x == y for x, y in zip(self, other)):
                    return True
            return False
        return NotImplemented

    def click(self):
        """
        Clicks on all selected elements.
        """

        for x in self:
            x.click()
        return self

    def filter(self, selector):
        """
        Return a filtered queryset with all elements that respect the current
        selector.
        """

        if callable(selector):
            selector_f = selector

        elif isinstance(selector, str):
            install_matches_selector_polyfill(self.parent)

            def selector_f(x):
                return x.method('matches', selector)

        elif isinstance(selector, Sequence):
            L = list(selector)

            def selector_f(x):
                return x in L

        data = self._unique([x for x in self if selector_f(x)])
        return QuerySet(data, self.parent)

    def find(self, selector):
        """
        Find sub-elements by CSS selector.
        """
        result = []
        for x in self:
            result.extend(x.find(selector))
        result = self._unique(result)
        return QuerySet(result, self.parent)

    def _unique(self, data):
        """
        Keep only unique elements in the sequence.
        """

        from sulfur.element import Element

        ids = set()
        result = []
        for x in data:
            if isinstance(x, Element):
                if x.selenium_id in ids:
                    continue
                else:
                    ids.add(x.selenium_id)
            result.append(x)
        return result


# Check: https://developer.mozilla.org/en/docs/Web/API/Element/matches
def install_matches_selector_polyfill(driver):
    driver.script('''
    if (!Element.prototype.matches) {
        Element.prototype.matches =
            Element.prototype.matchesSelector ||
            Element.prototype.mozMatchesSelector ||
            Element.prototype.msMatchesSelector ||
            Element.prototype.oMatchesSelector ||
            Element.prototype.webkitMatchesSelector ||
            function(s) {
                var matches = (this.document || this.ownerDocument).querySelectorAll(s),
                    i = matches.length;
                while (--i >= 0 && matches.item(i) !== this) {}
                return i > -1;
            };
    }''')
