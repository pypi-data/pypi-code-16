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


__all__ = ['MetaExtension', 'inject_meta']


def extract_meta(lines):
    """Extract metadata from markdown content.

    Args:
        lines (list of string): List of lines from the markdown content

    Returns:
        tuple: A two elements tupple.

        The first element is the parsed metadata or None if the document
        doesn't contains the metadata header.

        The second element is the markdown document without its metadata
        headers. The document is returned as a list of strings.
    """
    inside_meta = True
    meta = []
    new_lines = []

    # find first non empty line
    first_line = next((index for index, line in enumerate(lines) if line.strip()), 0)
    if lines[first_line] != '---':
        return None, lines

    for line in lines[first_line + 1:]:
        if line == '---':
            inside_meta = False
            continue

        if inside_meta:
            meta.append(line)
        else:
            if new_lines or not (not line and not new_lines):
                new_lines.append(line)

    return yaml.load('\n'.join(meta)), new_lines


class MetaPreprocessor(Preprocessor):
    def run(self, lines):
        self.markdown.meta, content_lines = extract_meta(lines)

        return content_lines


class MetaExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        md.preprocessors.add("yaml-meta", MetaPreprocessor(md), '>normalize_whitespace')


def makeExtension(*args, **kwargs):
    return MetaExtension(*args, **kwargs)


def inject_meta(md_content, meta, update=False):
    """Injects metadata into a markdown document.

    Args:
        md_content (string): Markdown content.
        meta (dict): Metadta to inject. If None, existing metadata will be
            removed
        update (bool): if set to True, any existing meta data in `md_content`
            will be upgrade with the `meta` dict.
            If False, metadata will be replaced.

    Returns:
        string: The updated markdown content.
    """
    old_meta, md_lines = extract_meta(md_content.splitlines())

    if meta is None:
        return '\n'.join(md_lines)

    if update is True:
        old_meta.update(meta)
        meta = old_meta

    return """---

{meta}
---

{content}
""".format(
        meta=yaml.dump(meta, default_flow_style=False, indent=4),
        content='\n'.join(md_lines))
