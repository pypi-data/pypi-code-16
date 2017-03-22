from collections import OrderedDict
from hashids import Hashids
import hashlib

from django.conf import settings
from django.db import models
from django.db.models import QuerySet


class DateTimeModelMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated')

    class Meta:
        abstract = True


# Add a computed property to model that generates a hashid
# that can be used to show unguessable IDs instead
# of the actual ID
class UIDManager(models.Manager):

    def get_by_uid(self, uid):
        id_ = self.model.hashids().decode(uid)
        obj = None
        if len(id_) > 0:
            try:
                obj = self.get(pk=id_[0])
            except models.ObjectDoesNotExist:
                pass

        return obj


class UIDMixin(models.Model):

    objects = UIDManager()

    _hashids = None

    def __init__(self, *args, **kwargs):
        super(UIDMixin, self).__init__(*args, **kwargs)

    @classmethod
    def hashids(cls):
        if not cls._hashids:
            md5 = hashlib.md5()
            md5.update('{}{}'.format(settings.SECRET_KEY, cls.__name__))
            cls._hashids = Hashids(salt=md5.hexdigest(), min_length=16)
        return cls._hashids

    @property
    def uid(self):
        return self.hashids().encode(self.pk)

    class Meta:
        abstract = True


def mptt_build_tree(queryset, children_key):
    '''
    :param queryset: the entire tree, or portion of tree, you're trying to construct
    :param children_key: key to store children, can't be a field name that's already on the model
    :return: QuerySet, with children (also QuerySets) properly nested to each level present
    '''
    nodes = OrderedDict()
    nodes_children = OrderedDict()

    for row in queryset:
        nodes[row.id] = row
        if nodes_children.get(row.parent_id):
            nodes_children[row.parent_id]._result_cache.append(row)
        else:
            nodes_children[row.parent_id] = QuerySet()
            nodes_children[row.parent_id]._result_cache = [row]

    for k, node in nodes.iteritems():
        # Try to find the parent so we can attach the child nodes
        setattr(node, children_key, QuerySet())
        children = getattr(node, children_key)
        children._result_cache = []
        if nodes.get(node.parent_id):
            children = getattr(nodes[node.parent_id], children_key)
            children._result_cache.append(node)

    # Build out root nodes for the base level of the list
    root_nodes = QuerySet()
    root_nodes._result_cache = []
    for node_id, node in nodes.iteritems():
        if node.parent_id is None:
            root_nodes._result_cache.append(node)

    return root_nodes


class MPTTDescendantsTreeMixin(object):

    def get_descendants_as_tree(self, children_key='children', **filters):
        return mptt_build_tree(self.get_descendants(include_self=True).filter(**filters), children_key=children_key)[0]
