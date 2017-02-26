# -*- coding: utf-8 -*-
import re

from pynlple.exceptions import TokenizationException


class IPreprocessor(object):
    """Interface to collect modules for text string preprocessing."""

    def preprocess(self, string_):
        return None


class Replacer(IPreprocessor):
    """Preprocessor interface for modules that replace certain text entities with normalized tags, etc."""


class StackingPreprocessor(IPreprocessor):
    """Class for continuous stacking and applying preprocessors in a natural order."""

    def __init__(self, preprocessor_list=list()):
        self.preprocessors = list(preprocessor_list)

    def append_preprocessor(self, preprocessor):
        self.preprocessors.append(preprocessor)

    def prepend_preprocessor(self, preprocessor):
        self.preprocessors.insert(0, preprocessor)

    def preprocess(self, string_):
        out_string = string_
        for preprocessor in self.preprocessors:
            out_string = preprocessor.preprocess(out_string)
        return out_string


class ToLowerer(Replacer):
    """Lowers all alpha characters."""

    def preprocess(self, string_):
        return string_.lower()


class RegexReplacer(Replacer):
    """Preprocessor. Replaces entities described by a specific regular expression from a text string
    with a stated string. Supports \n groups usage in target string."""

    def __init__(self, regex_query_string, target_string_with_groups, case_sensitive, use_locale, restrict_to_ascii):
        self.target = target_string_with_groups
        flag_1 = re.IGNORECASE if not case_sensitive else 0
        flag_2 = re.LOCALE if use_locale else 0
        flag_3 = re.ASCII if restrict_to_ascii else 0
        self.pattern = re.compile(regex_query_string, flag_1 | flag_2 | flag_3)
        super().__init__()

    def preprocess(self, string_):
        return re.sub(self.pattern, self.target, string_)


class RegexReplacerAdapter(RegexReplacer):

    def __init__(self, regex_query, replace_tag_with=None, case_sensitive=False, use_locale=False, restrict_to_ascii=False):
        if not replace_tag_with:
            replace_tag_with = ''
        super().__init__(regex_query, replace_tag_with, case_sensitive, use_locale, restrict_to_ascii)


class MultiWhitespaceReplacer(RegexReplacerAdapter):
    """Replace numerous whitespaces (\s+) in an input string with a default single space ' '."""

    def __init__(self, replace_tag_with=' '):
        regex_query = r'\s+'
        super().__init__(regex_query, replace_tag_with)


class Trimmer(Replacer):
    """Trims (or strips) heading and trailing whitespaces."""

    def preprocess(self, string_):
        return string_.strip()


class HtmlTagReplacer(RegexReplacerAdapter):
    """Replaces all tags of format <tag> and </tag> including tags with attributes and inner values: <a href='..'>."""

    def __init__(self, replace_tag_with=None):
        regex_query = r'<.*?>'
        super().__init__(regex_query, replace_tag_with)


class VKMentionReplacer(RegexReplacerAdapter):
    """Replaces the inner VK links and user mention of type '[<id>|<name>]'."""

    def __init__(self, replace_tag_with=None):
        regex_query = r'\[[\w_\-:]+\|.*\]'
        super().__init__(regex_query, replace_tag_with, False, False, False)


class AtReferenceReplacer(RegexReplacerAdapter):
    """Replaces the inner VK links and user mention of type '@<id>' (or '@<name>'?).
    This replacer finds only such entities which are separate words (start the line or
    have blank whitespace)"""

    def __init__(self, replace_tag_with=None):
        regex_query = r'((?<=\s)|(?<=^))@[\w_-]+'
        super().__init__(regex_query, replace_tag_with, False, False, False)


class URLReplacer(RegexReplacerAdapter):
    """Research https://mathiasbynens.be/demo/url-regex and https://gist.github.com/dperini/729294
    Since we need to increase recall of link-a-like entities in text, we adopt the algorithm with
    some possible erroneous cases.
    I used regexp from https://mathiasbynens.be/demo/url-regex by @stephenhay
    and extended with ftps, www, wwwDDD prefixes, and "\" variant of slash ("/")"""

    def __init__(self, replace_tag_with=None):
        regex_query = r'((ht|f)tps?:[\\/]+|www\d{0,3}\.)([.…]+|[^\s\\/$.?#].[^\s]*)'
        super().__init__(regex_query, replace_tag_with, False, False, False)


class EmailReplacer(RegexReplacerAdapter):
    """"""

    def __init__(self, replace_tag_with=None):
        regex_query = r'[\w0-9][\w0-9._%+-]{0,63}@(?:[\w0-9](?:[\w0-9-]{0,62}[\w0-9])?\.){1,8}[\w]{2,63}'
        super().__init__(regex_query, replace_tag_with, False, False, False)


class UserWroteRuReplacer(RegexReplacerAdapter):
    """"""
# ((\d\d\s\w\w\w\s\d\d\d\d|\w+)(,\s\d\d:\d\d)?)?
    def __init__(self, replace_tag_with=None):
        regex_query = r'[^\s]+\s(\(\d\d\.\d\d\.\d\d\s\d\d:\d\d\)\s)?писал\((а|a)\)\s?((\d\d\s\w\w\w\s\d\d\d\d|\w+)(,\s\d\d:\d\d)?\s?)?:'
        super().__init__(regex_query, replace_tag_with, False, False, False)


class DigitsReplacer(RegexReplacerAdapter):
    """Replaces all series of digits."""

    def __init__(self, multi, replace_tag_with=None):
        regex_query = r'\d+' if multi else r'\d'
        super().__init__(regex_query, replace_tag_with, False)


class QuotesReplacer(RegexReplacerAdapter):
    """Replaces variations of single qoute (actually there are not much of them,
    but there are some look-alike symbols from the top of the unicode table
    that resemble single quotes and may be used in its function.
    So, take care when using this class. Symbols replaced: ['`ʹʻʼʽ՚‘’‚‛′‵] to the
    default [']. Please, ref to http://unicode-table.com to decode symbols."""

    DEFAULT_REPLACEMENT = '\''

    def __init__(self, replace_tag_with=DEFAULT_REPLACEMENT):
        # Some of the symbols are taken from other than punctuation.txt section
        regex_query = r'[\'`ʹʻʼʽ՚‘’‚‛′‵]'
        # This section does not contain quotes from not-punctuation.txt section
        # regex_query = r'[\'‘’‚‛′‵]'
        super().__init__(regex_query, replace_tag_with, False, False, True)


class DoubleQuotesReplacer(RegexReplacerAdapter):
    """Replaces variations of double qoute (actually there are not much of them,
    but there are some look-alike symbols from the top of the unicode table
    that resemble double quotes and may be used in its function.
    So, take care when using this class. Symbols replaced: ["«»ʺ“”„‟″‶] to the
    default [\"]. Please, ref to http://unicode-table.com to decode symbols."""

    DEFAULT_REPLACEMENT = "\""

    def __init__(self, replace_tag_with=DEFAULT_REPLACEMENT):
        regex_query = r'["«»ʺ“”„‟″‶]'
        super().__init__(regex_query, replace_tag_with, False, False, True)


class DoubleQuotesEscaper(RegexReplacerAdapter):
    """Escapes the double qoutes symbol with the corresponding string tag"""

    DEFAULT_REPLACEMENT = "DQTS"

    def __init__(self, replace_tag_with=DEFAULT_REPLACEMENT):
        regex_query = r'\"'
        super().__init__(regex_query, replace_tag_with, False, False, True)


class DashAndMinusReplacer(RegexReplacerAdapter):
    """Replaces variations of dash/minus (actually there are not much of them,
    but there are some look-alike symbols from the top of the unicode table
    that resemble dash and minus and may be used in its function.
    So, take care when using this class. Symbols replaced: [-‐‑‒–—] to the
    default [-]. Please, ref to http://unicode-table.com to decode symbols."""

    def __init__(self, replace_tag_with='-'):
        regex_query = r'[-‐‑‒–—]'
        super().__init__(regex_query, replace_tag_with, False, False, True)


class SoftHyphenReplacer(RegexReplacerAdapter):
    """Replaces soft hyphen with nothing. Means - removes it."""

    def __init__(self, replace_tag_with=''):
        regex_query = r'[­]'
        super().__init__(regex_query, replace_tag_with, False)


class TripledotReplacer(RegexReplacerAdapter):
    """Replaces triple dot one-symbol expression with 3 separate fullstops."""

    def __init__(self, replace_tag_with='...'):
        regex_query = r'[…]'
        super().__init__(regex_query, replace_tag_with, False)


class BoldTagReplacer(RegexReplacerAdapter):

    def __init__(self, replace_tag_with=''):
        regex_query = r'</?b>'
        super().__init__(regex_query, replace_tag_with, False)


class MultiPunctuationReplacer(RegexReplacerAdapter):
    """Removes all multiple punctuation.txt (default keyboard set + some additional) usage
    according to regex r'[`~!@#$%^&*=+\(\)\[\]{}<>/|\\?\.…,№:;_-]'."""

    def __init__(self, replace_tag_with='\\1'):
        regex_query = r'([\'\"`~!@#$%^&*=+\(\)\[\]{}<>/|\\?\.…,№:;_-])\1+'
        super().__init__(regex_query, replace_tag_with, False, False, False)


class NonAlphaNumPuncWhitespaceAllUnicodeReplacer(RegexReplacerAdapter):
    """Replaces all unicode alpha-numeric, punctuation.txt (default keyboard set + some additional), and whitespaces
    according to regex r'[^\s\w\'\"`~!@#$%^&*=+\(\)\[\]{}<>/|\\?\.…,№:;_-]'."""

    def __init__(self, replace_tag_with=''):
        regex_query = r'[^\s\w\'\"`~!@#$%^&*=+\(\)\[\]{}<>/|\\?\.…,№:;_-]'
        super().__init__(regex_query, replace_tag_with, False, False, False)


class NonWordOrNumberOrWhitespaceAllUnicodeReplacer(RegexReplacerAdapter):
    """This cannot handle _ correctly. This also cannot handle soft hyphen correctly."""

    def __init__(self, replace_tag_with=' '):
        parts = [
            r'(?<=\d)[,:\.](?!\d)|(?<!\d)[,:\.](?=\d)|(?<!\d)[,:\.](?!\d)',  # this leaves out digital sequences with , : . in middle
            r'(?<=[\w\d])[\'\-](?![\w\d])|(?<![\w\d])[\'\-](?=[\w\d])|(?<![\w\d])[\'\-](?![\w\d])',  # this leaves out alphanumeric tokens with - and ' in middle
            r'[^\s\w\d\'\-,:\.]+',  # all other non-whitespace, non-alpha and non-digits
            r'_',
            ]
        regex_query = r'(' + r'|'.join(parts) + r')+'
        super().__init__(regex_query, replace_tag_with, False, False, False)


class WordTokenizer(RegexReplacerAdapter):
    """"""

    TOKEN_DEFUALT_DELIM = ' '

    def __init__(self, token_delim=TOKEN_DEFUALT_DELIM):
        token_types = [
            r'([^\W\d_]+([\'\-][^\W\d_]+)*[^\W\d_]*)',  # tokens, also with - and ' in middle
            r'([^\W_]+([\'\-][^\W\d_]+)+)',  # tokens, starting with number and ' - in middle ("7-fold", etc.)
            r'(\d+([,:.]\d+)*\d*)',  # digital sequences, also with , : . in middle
            # r'[^\W\d_]+',  # all other alpha tokens, excluding underscore
            # r'[\d\W]+',  # all other numeric sequences
            r'\.+',
            r'[^\w\d\s]',  # all individual symbols that are not alphanum or whitespaces
            r'_',  # underscore as being exluded by \w and previously by [^\W\d_]+
        ]
        regex_query = r'(' + r'|'.join(token_types) + r')'
        super().__init__(regex_query, token_delim, False, False, False)

    def preprocess(self, string_):
        res = []
        for matches in re.finditer(self.pattern, string_):
            # sorted_groups = sorted(matches.groups(), key=lambda g: len(g) if g else 0, reverse=True)
            # res.append(sorted_groups[0])
            # filtered = filter(lambda m: m.end() - m.start() != 0, matches)
            # if len(filtered) > 1:
            #     raise TokenizationException(__name__ + ' regex yielded multiple tokenization: ' + ','.join(filtered))
            # match = filtered[0]
            if matches.span()[1] - matches.span()[0] < 0:
                raise TokenizationException(__name__ + ' regex yielded incorrect tokenization:\r\n'
                                            + 'string:"' + string_
                                            + '", span:[' + str(matches.span()[0])
                                            + ',' + str(matches.span()[1]) + '], results:"'
                                            + ','.join(res) + '"')
            res.append(matches.string[matches.span()[0]:matches.span()[1]])
        return WordTokenizer.TOKEN_DEFUALT_DELIM.join(res)


class DefaultPreprocessorStack(StackingPreprocessor):
    def __init__(self):
        stack = [
                                        BoldTagReplacer(),
                                        URLReplacer(' urlTag '),
                                        HtmlTagReplacer(' '),
                                        VKMentionReplacer(' vkMentionTag '),
                                        EmailReplacer(' emailTag '),
                                        AtReferenceReplacer(' atRefTag '),
                                        UserWroteRuReplacer(' userWroteRuTag '),
                                        QuotesReplacer(),
                                        DoubleQuotesReplacer(),
                                        SoftHyphenReplacer(),
                                        DashAndMinusReplacer(),
                                        TripledotReplacer(),
                                        NonAlphaNumPuncWhitespaceAllUnicodeReplacer(' '),
                                        ToLowerer(),
                                        DigitsReplacer(False, '0'),
                                        MultiPunctuationReplacer(),
                                        MultiWhitespaceReplacer(),
                                        WordTokenizer(),
                                        Trimmer(),
                                        # Any other?
        ]
        super().__init__(stack)
