from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group

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

    # We could do this with django permissions, but we want them to be granular
    readGroup = models.ForeignKey(Group, null=True, blank=True,
                                  related_name='+')
    moveGroup = models.ForeignKey(Group, null=True, blank=True,
                                  related_name='+')
    addGroup = models.ForeignKey(Group, null=True, blank=True,
                                 related_name='+')
    deleteGroup = models.ForeignKey(Group, null=True, blank=True,
                                    related_name='+')
    manageGroup = models.ForeignKey(Group, null=True, blank=True,
                                    related_name='+')

    class Meta:
        permissions = (
            ("create_board", "Can create a order board"),
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

    class Meta:
        permissions = (
            ("modify_stages", "Can modify board stages"),
        )
