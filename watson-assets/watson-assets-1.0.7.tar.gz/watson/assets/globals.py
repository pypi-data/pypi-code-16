# -*- coding: utf-8 -*-


class Asset(object):
    def _render(self, tag, self_closing=True, trailing_slash=True, **kwargs):
        parts = ['<', tag]
        attrs = [' {}="{}"'.format(attr, value) for attr, value in kwargs.items()]
        parts.extend(attrs)
        if self_closing:
            if trailing_slash:
                parts.append(' /')
            parts.append('>')
        else:
            parts.extend(('<', tag, '>'))
        return ''.join(parts)

    def render(self, tag, self_closing=True, trailing_slash=True, **kwargs):
        return self._render(tag, self_closing, trailing_slash, **kwargs)

    def __call__(self, tag, self_closing=True, trailing_slash=True, **kwargs):
        return self.render(tag, self_closing, trailing_slash, **kwargs)

asset = Asset
