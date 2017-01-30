from jsonattrs.models import Schema


def template_xlang_labels(attr):
    try:
        labels = ['data-label-{}="{}"'.format(k, v)
                  for k, v in attr.items()]
        return ' '.join(labels)
    except AttributeError:
        return ''


class JsonAttrsMixin:
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        obj = self.object
        field = self.attributes_field
        obj_attrs = getattr(obj, field)

        schemas = Schema.objects.from_instance(obj)
        attrs = [a for s in schemas for a in s.attributes.all()]
        context[field] = [(a.long_name,
                           a.render(obj_attrs.get(a.name, '—')),
                           template_xlang_labels(a.long_name_xlat))
                          for a in attrs if not a.omit]
        return context
