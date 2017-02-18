
import re
import operator

try:
    from functools import reduce
except ImportError:
    pass

from django.db.models import Q


__all__ = ['normalize_query', 'build_query', 'model_search']


def normalize_query(query_string,
                    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    """
    Splits the query string in invidual keywords, getting rid of unecessary
    spaces and grouping quoted words together.
    Example:

    >>> normalize_query('  some random  words "with   quotes  " and   spaces')
    ['some', 'random', 'words', 'with quotes', 'and', 'spaces']
    """
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)]


def build_query(query_string, search_fields):
    """
    Returns a query, that is a combination of Q objects. That combination
    aims to search keywords within a model by testing the given search fields.
    """
    terms = normalize_query(query_string)

    if not terms:
        return None

    query = reduce(
        operator.__and__,
        (reduce(
            operator.__or__,
            (Q(**{"%s__icontains" % field_name: term})
             for field_name in search_fields)
        ) for term in terms),
    )
    return query


def model_search(query, queryset, fields):

    if not query:
        return queryset

    entry_query = build_query(query, fields)

    return queryset.filter(entry_query)
