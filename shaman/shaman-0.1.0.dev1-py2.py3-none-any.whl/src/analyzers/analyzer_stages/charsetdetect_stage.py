import re
import pickle

from shaman.src.analyzers.abstract_stage import AbstractStage


class CharsetDetectStage(AbstractStage):
    """
    Trying to detect a charset for a document. If no charset has been detected, returns utf-8.
    Based on a grab functon detect_charset (link: https://github.com/lorien/grab/blob/master/grab/document.py).
    Input data:
        - grab_obj
    Output data:
        - charset
    Using modules:
        - re (https://docs.python.org/2/library/re.html)
    """

    def __init__(self, config):
        super(CharsetDetectStage,self).__init__(config)
        self.order = config['order']

    def notIsAlias(self, ch1, ch2):
        for x in self.CH_ALIAS:
            if (ch1 in x) and (ch2 in x):
                return True
        return False

    def detect_charset(self, res):
        charset = []
        if res.body:
            chunk = res.body[:16384]
            charset_in_chunk = self.RE_META_CHARSET.search(chunk)
            if charset_in_chunk:
                charset.append(self.RE_META_CHARSET.search(chunk).group(1).decode(res.charset).lower())

            if res.body.startswith(b'<?xml'):
                match = self.RE_XML_DECLARATION.search(res.body)
                if match:
                    enc_match = self.RE_DECLARATION_ENCODING.search(match.group(0))
                    if enc_match:
                        charset.append(enc_match.group(1).decode(res.charset).lower())
            if 'Content-Type' in res.headers:
                pos = res.headers['Content-Type'].find('charset=')
                if pos > -1:
                    charset.append(res.headers['Content-Type'][(pos + 8):].split(';')[0].lower())
            if len(charset) == 1:
                return charset[0]
            elif len(charset) == 2:
                if charset[0] == charset[1]:
                    return charset[0]
                else:
                    return 'utf8'
            elif len(charset) == 3:
                if charset[0] == charset[1] == charset[2]:
                    return charset[0]
                else:
                    return 'utf8'
            else:
                return 'utf8'

    def do_stage(self, message):
        self.RE_XML_DECLARATION = re.compile(br'^[^<]{,100}<\?xml[^>]+\?>', re.I)
        self.RE_DECLARATION_ENCODING = re.compile(br'encoding\s*=\s*["\']([^"\']+)["\']')
        self.RE_META_CHARSET = \
            re.compile(br'<meta[^>]+content\s*=\s*[^>]+charset=([-\w]+)', re.I)
        self.KOV = set(['"', "'"])
        self.CH_ALIAS = [{'windows-1251', 'cp1251'}, {'utf8', 'utf-8'}]

        if 'output_dict' not in message.__dict__:
            message.charset = 'No results'
            return message
        else:
            if self.py_version == 2:
                message.grab_obj = pickle.loads(message.output_dict['response'].encode('utf-8'))
            else:
                message.grab_obj = pickle.loads(message.output_dict['response'])
            charset = self.detect_charset(message.grab_obj)
            message.charset = charset
            message.add_result_to_message('charset', charset, 'mongo_extra')
            return message