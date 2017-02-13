import re

from detectem.plugin import Plugin


class CrayonSyntaxHighlighterPlugin(Plugin):
    name = 'crayon_syntax_highlighter'
    homepage = 'https://wordpress.org/plugins-wp/crayon-syntax-highlighter/'

    matchers = [
        {
            'indicator': '/plugins/crayon-syntax-highlighter/js/min/crayon\.min\.js',
            'js_command': 'CrayonSyntaxSettings.version',
            'end_method': 'clean_version_from_js',
        }
    ]
    # http://reactore.com/generic-rest-api-services-using-akka-http/
    def get_version_from_js(self, output):
        match = re.findall('(\d.*)', output)
        if match:
            return match[0]
