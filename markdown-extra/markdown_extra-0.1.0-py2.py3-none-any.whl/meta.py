"""This extension adds metadata support inside markdown documents.

Metadata is a ``YAML`` formatted datastructure defined at the very beginning
of the document.
It must be defined between ``---`` YAML separators.
The first ``---`` must be the first line of the document to be correctly parsed.

Once the document is parsed, the metadata is save as a ``meta`` property of
the markdown instance used to convert the file.

.. doctest::

    >>> import markdown
    >>> md_content = '''---
    ...
    ...     author: "John Doe"
    ...     tags:
    ...       - "first-tag"
    ...       - "other-tag"
    ...
    ... ---
    ...
    ... First paragraph of the document goes here
    ... '''
    >>> md = markdown.Markdown(extensions=['markdown_extra.meta'])
    >>> html = md.convert(md_content)
    >>> md.meta['author']
    'John Doe'
    >>> md.meta['tags']
    ['first-tag', 'other-tag']

"""

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
import yaml


__all__ = ['MetaExtension']


class MetaPreprocessor(Preprocessor):
    def run(self, lines):
        self.markdown.meta = None
        inside_meta = True
        meta = []
        new_lines = []

        if lines[0] != '---':
            return lines

        for line_nb, line in enumerate(lines):
            # skip first line as we already know it's the delimiter
            if line_nb == 0:
                continue

            # end of meta
            if line == '---':
                inside_meta = False
                continue

            if inside_meta:
                meta.append(line)
            else:
                # prevent appending empty lines following the meta header
                if new_lines or not (not line and not new_lines):
                    new_lines.append(line)

        self.markdown.meta = yaml.load('\n'.join(meta))

        return new_lines


class MetaExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        md.preprocessors.add("yaml-meta", MetaPreprocessor(md), '>normalize_whitespace')


def makeExtension(*args, **kwargs):
    return MetaExtension(*args, **kwargs)
