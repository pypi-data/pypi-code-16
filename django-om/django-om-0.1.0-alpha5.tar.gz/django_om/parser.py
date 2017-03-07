from inspect import isfunction

from django.db.models import Manager
from transit.transit_types import Symbol

from django_om import settings

READS = settings.PARSER['READS']
MUTATIONS = settings.PARSER['MUTATIONS']


class Read(object):
    def __init__(self, field, params=None):
        self.params = params or {}
        self.field = field

    def _run(self, request, field):
        read = READS[field]
        if isfunction(read):
            # Custom read function
            result = READS[field](
                request=request, params=self.params
            )
        else:
            reads = [f for f in read._meta.fields]
            result = Join(self.field, reads).run(request)
        return result

    def run(self, request, obj=None):
        result = None
        if obj:
            result = getattr(obj, self.field)
        else:
            if self.field in READS:
                return self._run(request, self.field)
            elif "/" in self.field:
                key, _ = self.field.split("/")
                return self._run(request, key)
        return result

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        if self.params:
            return 'Read({0}, params={1})'.format(self.field, self.params)
        else:
            return 'Read({0})'.format(self.field)

    def __unicode__(self):
        return unicode(self.__str__())


class Join(object):
    def __init__(self, key, fragments, params=None):
        self.params = params or {}
        self.key = key
        self.reads = []
        self.joins = []
        for fragment in fragments:
            parsed = Query.parse_fragment(fragment)
            if isinstance(parsed, Read):
                self.reads.append(parsed)
            elif isinstance(parsed, Join):
                self.joins.append(parsed)

    def _run(self, request, obj):
        new_object = {}
        for r in self.reads:
            new_object[r.field] = r.run(request, obj)
        for j in self.joins:
            new_object[j.key] = j.run(request, obj)
        return new_object

    def run(self, request, obj=None):
        user = request.user

        key = self.key
        specifier = None
        if '/' in key:
            key, specifier = key.split('/')

        if obj:
            attr = getattr(obj, self.key)
            if isinstance(attr, Manager):
                objects = attr.all()
            else:
                return self._run(request, attr)
        else:
            try:
                model = READS[key]
            except KeyError:
                return self._run(request, None)

            objects = model.objects

        objects = objects.authorize_for(user) if hasattr(
            objects, 'authorize_for'
        ) else objects

        where = self.params.get('where')
        sort = self.params.get('sort')
        offset = self.params.get('offset', 0)
        limit = self.params.get('limit', settings.PAGE_SIZE)

        if where:
            for k, v in where.items():
                objects = objects.filter(**{k: v})

        if sort:
            objects = objects.order_by(sort)

        objects = list(objects[offset:offset + limit])

        result = []
        for obj in objects:
            result.append(self._run(request, obj))

        if specifier == 'detail':
            result = result[0]

        return result

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        if self.params:
            return 'Join({0}, {1}, params={2})'.format(
                self.key, self.reads + self.joins, self.params
            )
        else:
            return 'Join({0}, {1})'.format(self.key, self.reads + self.joins)

    def __unicode__(self):
        return unicode(self.__str__())


class Mutation(object):
    def __init__(self, symbol, params):
        self.symbol = symbol
        self.params = params

    def run(self, request):
        mutate = MUTATIONS[str(self.symbol)]
        if isfunction(mutate):
            # Custom mutate function
            result = mutate(request, self.params)
        else:
            if self.params.get('id'):
                instance = mutate.objects.get(pk=self.params['id'])
            else:
                instance = mutate(**self.params)
                instance.save()
            result = True
        return result

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return 'Mutation({0}, {1})'.format(self.symbol, self.params)

    def __unicode__(self):
        return unicode(self.__str__())


class Query(object):
    def __init__(self, query):
        self.fragments = []
        if isinstance(query, list):
            for fragment in query:
                self.fragments.append(self.parse_fragment(fragment))
        else:
            self.fragments = [self.parse_fragment(query)]

    @classmethod
    def parse_fragment(self, fragment, params=None):
        if isinstance(fragment, list):
            # Parameterized
            result = self.parse_fragment(fragment[0], fragment[1])
        elif isinstance(fragment, dict):
            if len(fragment) == 1:
                # Join
                key, reads = fragment.items()[0]
                result = Join(key, reads, params)
            else:
                # Union
                raise NotImplementedError("Union queries are not implemented")
        elif isinstance(fragment, Symbol):
            # Mutation
            result = Mutation(fragment, params)
        else:
            # Read (Keyword)
            result = Read(fragment, params)
        return result

    def __str__(self):
        return 'Query({0})'.format(self.fragments)

    def __unicode__(self):
        return unicode(self.__str__())

    def run(self, request):
        response = {}
        for fragment in self.fragments:
            if isinstance(fragment, Join):
                response[fragment.key] = fragment.run(request)
            elif isinstance(fragment, Read):
                response[fragment.field] = fragment.run(request)
            elif isinstance(fragment, Mutation):
                response.update(fragment.run(request))
        return response
