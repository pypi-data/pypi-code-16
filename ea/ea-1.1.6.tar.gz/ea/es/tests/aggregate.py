from ea import es
import ea.schema



class TestEntity(es.Entity):
    foo = ea.schema.fields.String()
    bar = ea.schema.fields.String()
    baz = ea.schema.fields.String()


class TestValueObject(es.ValueObject):
    foo = ea.schema.fields.String()
    bar = ea.schema.fields.String()
    baz = ea.schema.fields.String()


class TestAggegrate(es.Aggregate):
    __aggregatename__ = 'TestAggregate'

    entity = es.EntityField(TestEntity)
    valueobject = es.ValueObjectField(TestValueObject,
        many=True)
    default = ea.schema.fields.Boolean(default=False)

    def __init__(self):
        self.arg = None

    def missing(self):
        self.events.publish('Missing')

    def foo(self, arg):
        self.events.publish('Foo', arg=arg)

    def on_foo(self, event):
        self.arg = event.arg


class TestRepository(es.Repository):

    def __init__(self):
        self.rollback_invoked = False
        self.commit_invoked = False
        self.begin_invoked = False
        self.flush_invoked = False
        self.uow = set()

    def begin(self):
        self.begin_invoked = True

    def commit(self):
        self.commit_invoked = True

    def flush(self):
        self.flush_invoked = True

    def rollback(self):
        self.rollback_invoked = True

    def unitofwork(self):
        return self.uow
