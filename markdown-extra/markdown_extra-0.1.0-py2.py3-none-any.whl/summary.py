"""This extension is used to extract a summary from a markdown file.

A summary is a paragraph tagged with a ``[summary]`` element in its first line.
The summary won't be rendered in the final HTML document.
After the parsing occures, the summary can be accessed in a ``summary``
property of the markdown instance used.

This first paragraph will not be rendered.


.. doctest::

    >>> import markdown
    >>> md_content = '''
    ... [summary]
    ... This is the summary.
    ... It says very important stuff.
    ...
    ... This is the first paragraph of the document.
    ... '''
    >>> md = markdown.Markdown(extensions=['markdown_extra.summary'])
    >>> md.convert(md_content)
    '<p>This is the first paragraph of the document.</p>'
    >>> md.summary
    'This is the summary.\\nIt says very important stuff.'

If no ``summary`` tag is found in the document, the first paragraph will be
set in the ``summary`` property of the markdown instance.
In this case, the paragraph will not be removed from the final HTML produced.

"""

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
from markdown.treeprocessors import Treeprocessor


__all__ = ['SummaryExtension']


class SummaryPreprocessor(Preprocessor):
    """This processors will extract the [summary] tagged paragraph if existing
    and store its content in a *summary* attribute of the markdown instance.
    """
    def run(self, lines):
        inside_summary = False
        new_lines = []
        summary = []

        for line in lines:
            if line.strip() == '[summary]':
                inside_summary = True
                continue
            elif inside_summary and not line.strip():
                inside_summary = False
                continue

            if inside_summary:
                summary.append(line)
            else:
                new_lines.append(line)

        if summary:
            self.markdown.summary = '\n'.join(summary)
        else:
            self.markdown.summary = None

        return new_lines


class SummaryTreeProcessor(Treeprocessor):
    """If the *summary* of markdown instance is not set, extracts the first
    paragraph of the tree and uses its text as the summary.
    """
    def run(self, root):
        if not hasattr(self.markdown, 'summary'):
            self.markdown.summary = None

        if self.markdown.summary is not None:
            return root

        p = root.find('p')

        if p is not None:
            self.markdown.summary = ''.join(p.itertext())

        return root


class SummaryExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        md.preprocessors.add('summary', SummaryPreprocessor(md), '_end')
        md.treeprocessors.add('summary', SummaryTreeProcessor(md), '_end')


def makeExtension(**kwargs):
    return SummaryExtension(**kwargs)
