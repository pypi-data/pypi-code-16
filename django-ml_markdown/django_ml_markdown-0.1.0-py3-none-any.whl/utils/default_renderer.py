"""
    Default renderer module
"""
from django.utils.text import slugify
from misaka import HtmlRenderer
from pygments import highlight
from pygments.lexers import get_lexer_by_name, get_lexer_for_filename, ClassNotFound
from pygments.formatters.html import HtmlFormatter


class DefaultRenderer(HtmlRenderer):
    """
        Default Html renderer.
        Provides:
            * id attribute to h* tags (for readable anchor links in tables of contents)
            * syntax highlighting with extra syntax for fenced code
    """

    def header(self, content, level):
        """
            Parse headers

            :params content: That will be detween <h*> and </h*>
            :params level: The title level

            :return: a <h*> tag with slugified content as id
        """
        return '<h{n} id="{id}">{title}</h{n}>'.format(
            n=level,
            title=content,
            id=slugify(content)
        )

    def blockcode(self, text, lang=''):
        """
            Generate a syntax highlighted blockcode

            :param text: the code
            :param lang: the language, can be a language name, a filename, or
                an association of the two (ex: djangohtml:template.html)

            :return: the syntax highlighted block code
        """

        formatter = HtmlFormatter(nowrap=True)

        output_template = (
            '<div class="blockcode">'
            '{tab}'
            '<pre><code>{code}</code></pre>'
            '</div>'
        )

        tab_template = '<div class="blockcode-tab">{name}</div>'
        language = 'text'
        tab_name = ''

        if not lang:
            pass

        elif ':' in lang:
            tmp = lang.split(':')
            language, tab_name = tmp[0], ':'.join(tmp[1:])

        elif '.' in lang:
            tab_name = lang
            language = lang

        else:
            language = lang

        try:
            lexer = get_lexer_by_name(language, stripall=True)
        except ClassNotFound:
            try:
                lexer = get_lexer_for_filename(language, stripall=True)
            except ClassNotFound:
                lexer = get_lexer_by_name('text')

        return output_template.format(
            tab=tab_template.format(name=tab_name) if tab_name else '',
            code=highlight(text, lexer, formatter)
        )
