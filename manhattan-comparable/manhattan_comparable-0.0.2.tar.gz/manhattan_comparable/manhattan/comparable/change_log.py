from mongoframes import *
from datetime import date

__all__ = ['ChangeLogEntry']


class ChangeLogEntry(Frame):
    """
    The `ComparableFrame` class tracks changes to documents through entries in a
    change log. The `ChangeLogEntry` class is provided as a base class for
    implementing a change log but can also be used directly.
    """

    _fields = {
        'created',
        'documents',
        'documents_sticky_label',
        'user',
        'user_sticky_label',
        'type',
        'details'
        }

    # A set of HTML templates used to output the *diff* for a change log entry
    _templates = {
        'add': '''
<div class="change change--add">
    <div class="change__field">{field}</div>
    <div class="change__values">
        <div class="change__value change__value--new">
            {new_value}
        </div>
    </div>
</div>
            '''.strip(),

        'update': '''
<div class="change change--update">
    <div class="change__field">{field}</div>
    <div class="change__values">
        <div class="change__value change__value--original">
            {original_value}
        </div>
        <div class="change__value change__value--new">
            {new_value}
        </div>
    </div>
</div>
            '''.strip(),

        'delete': '''
<div class="change change--delete">
    <div class="change__field">{field}</div>
    <div class="change__values">
        <div class="change__value change__value--original">
            {original_value}
        </div>
    </div>
</div>
            '''.strip(),

        'note': '<div class="change change--note">{note}</div>'
        }

    @property
    def diff_html(self):
        """Return the entry's diff in HTML format"""
        return self.diff_to_html(self.details)

    @property
    def is_diff(self):
        """Return True if there are any differences logged for the entry"""
        if not isinstance(self.details, dict):
            return False

        for key in ['additions', 'updates', 'deletions']:
            if self.details.get(key, None):
                return True

        return False

    def add_diff(self, original, new):
        """
        Set the details of the change log entry as the difference between two
        dictionaries (original vs. new). The change log uses the following
        format:

            {
                'additions': {
                    'field_name': 'value',
                    ...
                },
                'updates': {
                   'field_name': ['original_value', 'new_value'],
                    ...
                },
                'deletions': {
                    'field_name': ['original_value']
                }
            }

        Values are tested for equality, there is special case handling for
        `Frame` class instances (see `diff_safe`) and fields with the word
        password in their name are redacted.

        NOTE: Where possible use diff structures that are flat, performing a
        diff on a dictionary which contains sub-dictionaries is not recommended
        as the verbose output (see `diff_to_html`) is optimized for flat
        structures.
        """
        changes = {}

        # Check for additions and updates
        for new_key, new_value in new.items():

            # Additions
            if new_key not in original:
                if 'additions' not in changes:
                    changes['additions'] = {}
                new_value = self.diff_safe(new_value)
                changes['additions'][new_key] = new_value

            # Updates
            elif original[new_key] != new_value:
                if 'updates' not in changes:
                    changes['updates'] = {}

                original_value = self.diff_safe(original[new_key])
                new_value = self.diff_safe(new_value)

                changes['updates'][new_key] = [original_value, new_value]

                # Check for password type fields and redact them
                if 'password' in new_key:
                    changes['updates'][new_key] = ['*****', '*****']

        # Check for deletions
        for original_key, original_value in original.items():
            if original_key not in new:
                if 'deletions' not in changes:
                    changes['deletions'] = {}

                original_value = self.diff_safe(original_value)
                changes['deletions'][original_key] = original_value

        self.details = changes

    def add_note(self, note):
        """Add a note as the entries details"""
        self.details = {'note': note}

    @classmethod
    def diff_to_html(cls, details):
        """Return the given set of details as HTML"""
        changes = []

        # Check that there are details to convert to HMTL
        if not details:
            return ''

        def _frame(value):
            """
            Handle converted `Frame` references where the human identifier is
            stored against the `_str` key.
            """
            if isinstance(value, dict) and '_str' in value:
                return value['_str']
            elif isinstance(value, list):
                return ', '.join([_frame(v) for v in value])
            return str(value)

        # Additions
        fields = sorted(details.get('additions', {}))
        for field in fields:
            new_value = _frame(details['additions'][field])
            if isinstance(new_value, list):
                new_value = ', '.join([_frame(v) for v in new_value])

            change = cls._templates['add'].format(
                field=field,
                new_value=new_value
                )
            changes.append(change)

        # Updates
        fields = sorted(details.get('updates', {}))
        for field in fields:
            original_value = _frame(details['updates'][field][0])
            if isinstance(original_value, list):
                original_value = ', '.join([_frame(v) for v in original_value])

            new_value = _frame(details['updates'][field][1])
            if isinstance(new_value, list):
                new_value = ', '.join([_frame(v) for v in new_value])

            change = cls._templates['update'].format(
                field=field,
                original_value=original_value,
                new_value=new_value
                )
            changes.append(change)

        # Deletions
        fields = sorted(details.get('deletions', {}))
        for field in fields:
            original_value = _frame(details['deletions'][field])
            if isinstance(original_value, list):
                original_value = ', '.join([_frame(v) for v in original_value])

            change = cls._templates['delete'].format(
                field=field,
                original_value=original_value
                )
            changes.append(change)

        # Note
        if 'note' in details:
            changes.append(cls._templates['note'].format(note=details['note']))

        return '\n'.join(changes)

    @classmethod
    def diff_safe(cls, value):
        """Return a value that can be safely stored as a diff"""
        if isinstance(value, Frame):
            return {'_str': str(value), '_id': value._id}
        elif isinstance(value, (list, tuple)):
            return [cls.diff_safe(v) for v in value]
        return value

    @staticmethod
    def _on_insert(sender, frames):
        for frame in frames:

            # Record *sticky* labels for the change so even if the documents or
            # user are removed from the system their details are retained.
            pairs = [(d, d.__class__.__name__) for d in frame.documents]
            frame.documents_sticky_label = ', '.join(
                ['{0} ({1})'.format(*p) for p in pairs]
                )

            if frame.user:
                frame.user_sticky_label = str(frame.user)


ChangeLogEntry.listen('insert', ChangeLogEntry.timestamp_insert)
ChangeLogEntry.listen('insert', ChangeLogEntry._on_insert)
