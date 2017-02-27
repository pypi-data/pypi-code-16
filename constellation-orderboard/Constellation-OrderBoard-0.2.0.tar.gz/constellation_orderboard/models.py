from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group

from guardian.shortcuts import assign_perm, remove_perm, get_perms


class Card(models.Model):
    name = models.CharField(max_length=128)
    quantity = models.IntegerField(default=1)
    units = models.CharField(max_length=128, blank=True)
    notes = models.TextField(blank=True)
    stage = models.ForeignKey('Stage', blank=True, null=True)
    board = models.ForeignKey('Board', blank=True, null=True)
    archived = models.BooleanField(default=False)


class Board(models.Model):
    name = models.CharField(max_length=128)
    desc = models.TextField()
    archived = models.BooleanField(default=False)

    def set_board_permissions(self, groups):
        permcodenames = []
        for node in Board._meta.permissions:
            permcodenames.append(node[0])

        for groupname, level in groups:
            if groupname.startswith('group-'):
                # This step gets the group name as it should be shown
                group = groupname.replace('group-', '', 1)
                group = Group.objects.get(pk=group)

                # This step in a compound action converts the type to int
                # and also reduces the index.  This accounts for the fact
                # that the 0th index is 'no permissions'.
                level = int(level) - 1

                # Switch on permissions level
                if level == 0:
                    # If the level is zero, we should remove all
                    # permissions
                    for perm in permcodenames:
                        remove_perm(perm, group, self)
                else:
                    # Add all the newly assigned perms
                    for perm in permcodenames[:level]:
                        assign_perm(perm, group, self)
                    # Remove any perms that aren't supposed to be here
                    for perm in permcodenames[level:]:
                        remove_perm(perm, group, self)

    def get_board_permissions(self):
        groups = []
        permcodenames = []
        for node in Board._meta.permissions:
            permcodenames.append(node[0])

        for group in Group.objects.all():
            level = len(set(
                get_perms(group, self)).intersection(set(permcodenames))) + 1

            groups.append({
                'name': group.name,
                'id': group.id,
                'level': level
            })

        return groups

    class Meta:
        permissions = (
            ("action_read_board", "Can read an order board"),
            ("action_add_cards", "Can add cards to an order board"),
            ("action_move_cards", "Can move cards on an order board"),
            ("action_archive_cards", "Can archive cards from an order board"),
            ("action_manage_board", "Can manage an order board"),
        )


class Stage(models.Model):
    name = models.CharField(max_length=128)
    index = models.IntegerField()
    archived = models.BooleanField(default=False)

    # Custom save method to verify constraints on the index
    # that we can't do at the database level
    def save(self, *args, **kwargs):
        if Stage.objects.first() is None:
            # First stage added
            self.index = 0
        elif self.index == -1:
            # Auto-fill for a new stage
            self.index = Stage.objects.aggregate(
                models.Max('index'))['index__max'] + 1
        else:
            stage_at_index = Stage.objects.filter(index=self.index).first()
            # Check uniqueness
            if stage_at_index is not None and stage_at_index != self:
                raise ValidationError("Index is already in use.")

            # Check for gaps
            if (self.index != 0 and
                Stage.objects.filter(index=self.index-1).first() is None):
                raise ValidationError("Index is not adjacent to another stage.")

        super(Stage, self).save(*args, **kwargs)

    def swap(self, otherStage):
        self.index, otherStage.index = otherStage.index, self.index

        # Save each one without checking uniqueness
        super(Stage, self).save()
        super(Stage, otherStage).save()
