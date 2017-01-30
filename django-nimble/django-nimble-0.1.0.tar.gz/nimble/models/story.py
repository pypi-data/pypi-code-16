from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

import reversion
from markdownx.models import MarkdownxField
from polymorphic.models import PolymorphicModel

from nimble.utilities.bootstrap_diffs import bootstrap_diffs


@reversion.register()
class Story(PolymorphicModel):

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = MarkdownxField(default='')
    typename = 'Story'

    def name(self):
        return '{}{:0>5}'.format(self.ident, self.id)

    def api_url(self):
        return reverse(self.api_detail_name, kwargs={
            'pk': self.pk,
        })

    @classmethod
    def api_keys(cls):
        return ['url', 'author', 'title', 'description']

    @classmethod
    def api_list_url(cls):
        return reverse(cls.api_list_name)

    @classmethod
    def create(cls, author, **kwargs):
        with reversion.create_revision():
            created_object = cls.objects.create(
                author=author, **kwargs
            )
            reversion.set_user(author)
            reversion.set_comment(
                "Created {}".format(cls.typename)
            )
        return created_object

    def update(self, user, data):
        with reversion.create_revision():
            for key, value in data.items():
                setattr(self, key, value)
            self.save()
            reversion.set_user(user)
            reversion.set_comment(
                "Edited {} through web".format(self.typename)
            )

    def versions(self):
        return reversion.models.Version.objects.get_for_object(self)

    def revision_numbers(self):
        return sorted([a.revision.id for a in self.versions()])

    def values_at_revision(self, revision):
        return self.versions().filter(revision__id=revision).first().field_dict

    def differences_between_revisions(self, older, newer):
        differences = {}
        new = self.values_at_revision(newer)
        old = self.values_at_revision(older)
        for key in set(new.keys()) | set(old.keys()):
            new_value = new.get(key)
            old_value = old.get(key)
            if new_value != old_value:
                differences[key] = {
                    'new': new_value,
                    'old': old_value,
                }
        return differences

    def difference_tables_between_revisions(self, older, newer):
        deltas = self.differences_between_revisions(older, newer)
        differences = {}
        for key, diffs in deltas.items():
            differences[key] = bootstrap_diffs(
                str(diffs['old']).split('\n'),
                str(diffs['new']).split('\n'),
            )
        return differences
