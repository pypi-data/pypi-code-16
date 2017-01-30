from collections import namedtuple
from difflib import Differ

from django.utils.html import format_html
from django.utils.safestring import mark_safe

Difference = namedtuple('Difference', ['line', 'tag'])
Inline = namedtuple('Inline', ['line1', 'line2', 'tags1', 'tags2'])


class MyDiff(Differ):
    def _dump(self, tag, x, lo, hi):
        """Generate comparison results for a same-tagged range."""
        for i in range(lo, hi):
            yield Difference(line=x[i], tag=tag)

    def _qformat(self, aline, bline, atags, btags):
        yield Inline(
            line1=aline, line2=bline,
            tags1=[i for i, b in enumerate(atags) if b.strip()],
            tags2=[i for i, b in enumerate(btags) if b.strip()],
        )


def strong_tag(text, highlights):
    html = format_html('')
    active = False
    for index, char in enumerate(text):
        if index in highlights and not active:
            html = format_html('{}{}', html, mark_safe('<strong>'))
            active = True
        if index not in highlights and active:
            html = format_html('{}{}', html, mark_safe('</strong>'))
            active = False
        html = format_html('{}{}', html, char)
    return html


def format_row(tag, row_class, text):
    return format_html(
        '<tr class="{}" style="font-family:monospace;">'
        '<td>{}</td><td>{}</td>'
        '</tr>',
        row_class, tag, text
    )


def bootstrap_diffs(first_lines, second_lines):
    table = format_html('<table class="table">')
    a = MyDiff()
    plus_tag = mark_safe(
        '<span class="glyphicon glyphicon-plus" aria-hidden="true"></span>'
    )
    minus_tag = mark_safe(
        '<span class="glyphicon glyphicon-minus" aria-hidden="true"></span>'
    )
    for index, diff in enumerate(
        a.compare(first_lines, second_lines), start=1
    ):
        if isinstance(diff, Difference):
            if diff.tag == '+':
                row_class = 'success'
                tag = plus_tag
            elif diff.tag == '-':
                row_class = 'danger'
                tag = minus_tag
            else:
                row_class = 'blank'
                tag = ''
            table = format_html(
                '{}{}',
                table,
                format_row(tag, row_class, diff.line)
            )
        else:
            line1 = strong_tag(diff.line1, diff.tags1)
            line2 = strong_tag(diff.line2, diff.tags2)
            row_class = 'warning'
            table = format_html(
                '{}{}{}',
                table,
                format_row(minus_tag, row_class, line1),
                format_row(plus_tag, row_class, line2),
            )
    return format_html('{}</table>', table)
