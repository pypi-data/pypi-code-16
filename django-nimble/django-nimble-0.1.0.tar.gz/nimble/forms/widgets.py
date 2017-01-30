from django.forms import widgets
from markdownx.widgets import MarkdownxWidget


class NeverRequiredCheckbox(widgets.CheckboxInput):
    def use_required_attribute(self, initial):
        return False


class ToggleableMarkdownWidget(widgets.MultiWidget):
    def __init__(self, attrs=None):
        # create choices for days, months, years
        # example below, the rest snipped for brevity.
        if attrs is not None:
            checkbox_attrs = attrs.copy()
        else:
            checkbox_attrs = {}
        checkbox_attrs['class'] = 'markdowntoggle'
        checkbox_attrs['checked'] = False
        checkbox_attrs['required'] = False
        checkbox_attrs['data-toggle'] = "toggle"
        checkbox_attrs['data-size'] = "mini"
        eye = "<span class='glyphicon glyphicon-eye-open' aria-hidden='true'></span>"  # noqa
        edit = "<span class='glyphicon glyphicon-pencil' aria-hidden='true'></span>"  # noqa
        checkbox_attrs['data-off'] = eye
        checkbox_attrs['data-on'] = edit
        _widgets = (
            NeverRequiredCheckbox(attrs=checkbox_attrs),
            MarkdownxWidget(attrs=attrs),
        )
        super().__init__(_widgets, attrs)

    def decompress(self, value):
        return [False, value]

    def format_output(self, rendered_widgets):
        return '<div class="markdowntogglediv"><div>{}</div>{}</div>'.format(
            *rendered_widgets
        )

    def render(self, *args, **kwargs):
        return super().render(*args, **kwargs)

    def value_from_datadict(self, data, files, name):
        return self.widgets[1].value_from_datadict(
            data, files, name + '_1'
        )

    class Media:
        js = (
            'nimble/js/togglemarkdownx.js',
        )
