# For what needed this module? No one really knows :D
# Maybe need remove this...


class Tag(object):
    def __init__(self, tag=None, single=False, content=None, tag_class=None, tag_id=None, **kwargs):
        if tag is None:
            self.tag = self.__class__.__name__.lower()
        else:
            self.tag = tag
        self.single = single

        if isinstance(tag_class, str):
            tag_class = tag_class.split(' ')
        assert isinstance(tag_class, (list, tuple, type(None)))
        if isinstance(tag_id, str):
            tag_id = tag_id.split(' ')
        assert isinstance(tag_id, (list, tuple, type(None)))

        kwargs.update({
            'class': tag_class,
            'id': tag_id
        })
        self.params = kwargs

        if content is None:
            content = []
        elif isinstance(content, str):
            content = [content]

        assert isinstance(content, list)
        self.content = content

    def select_all(self, match):
        if match == self.tag:
            yield self
        elif match.startswith('.'):
            tag_class = self.params.get('class', []) or []
            if match[1:] in tag_class:
                yield self
        elif match.startswith('#'):
            tag_id = self.params.get('id', []) or []
            if match[1:] in tag_id:
                yield self
        for item in self.content:
            if isinstance(item, Tag):
                temp = item.select_all(match)
                if hasattr(temp, '__iter__'):
                    for child in temp:
                        yield child

    def select(self, match):
        try:
            temp = self.select_all(match).__next__()
        except StopIteration:
            temp = None
        return temp

    def select_all_items(self, match):
        return list(self.select_all(match))

    def insert(self, element):
        if not self.single:
            self.content.append(element)
        else:
            raise Exception('Single tag has no space for content')

    def _stringify_content(self, splitter=''):
        for item in self.content:
            if isinstance(item, str):
                yield item
            elif hasattr(item, 'stringify'):
                yield item.stringify(splitter)
            else:
                yield str(item)

    def get_content(self, splitter=''):
        assert isinstance(splitter, str)
        return splitter.join(self._stringify_content(splitter))

    def stringify(self, splitter=''):
        data = (self.tag + ' ' +
                ', '.join(['{}={}'.format(param, value) for param, value in self._parse_params()])).strip()
        if self.single:
            return '<{data} />'.format(data=data)
        content = self.get_content(splitter)
        if len(content):
            content = splitter + content + splitter
        return '<{data}>{content}</{tag}>'.format(data=data, tag=self.tag,
                                                  content=content)

    def _parse_params(self):
        """
        Generator of tag params
        :return:
        """
        for param, value in sorted(self.params.items(), key=lambda item: item[0]):
            if value is not None:
                if isinstance(value, (list, tuple)):
                    value = ' '.join(value)
                if isinstance(value, dict):
                    value = '; '.join(['{}: {}'.format(k, v) for k, v in sorted(value.items(), key=lambda k: k[0])])
                if isinstance(value, str):
                    value = '"' + value + '"'
                else:
                    value = str(value)
                yield param, value

    def __str__(self):
        return self.stringify()

    def __repr__(self):
        return '<HtmlTag "{}">'.format(self.tag)


class Html(Tag):
    def __init__(self, content=None, **kwargs):
        super(Html, self).__init__(
            tag='html',
            content=content,
            **kwargs
        )


class Head(Tag):
    def __init__(self, content=None, **kwargs):
        super(Head, self).__init__(
            tag='head',
            content=content,
            **kwargs
        )


class Body(Tag):
    def __init__(self, content=None, **kwargs):
        super(Body, self).__init__(
            tag='body',
            content=content,
            **kwargs
        )


class A(Tag):
    def __init__(self, display, tag_class=None, tag_id=None, accesskey=None, coords=None, download=None, href=None,
                 hreflang=None, name=None, rel=None, rev=None, shape=None, tabindex=None, target=None, title=None,
                 type=None, **kwargs):
        super(A, self).__init__(
            tag='a',
            single=False,
            tag_class=tag_class,
            tag_id=tag_id,
            accesskey=accesskey,
            coords=coords,
            download=download,
            href=href,
            hreflang=hreflang,
            name=name,
            rel=rel,
            rev=rev,
            shape=shape,
            tabindex=tabindex,
            target=target,
            title=title,
            type=type,
            **kwargs
        )
        self.insert(display)


class Comment(Tag):
    def __init__(self, content):
        super(Comment, self).__init__(tag='comment', content=content)

    def stringify(self, splitter=''):
        return '<!-- {} -->'.format(self.get_content(splitter))


class Div(Tag):
    pass


class Img(Tag):
    def __init__(self, tag_class=None, tag_id=None, align=None, alt=None, border=None, height=None, hspace=None,
                 ismap=None, longdesc=None, lowsrc=None, src=None, vspace=None, width=None, usemap=None, **kwargs):
        super(Img, self).__init__(
            tag='img',
            tag_class=tag_class,
            tag_id=tag_id,
            single=True,
            align=align,
            alt=alt,
            border=border,
            height=height,
            hspace=hspace,
            ismap=ismap,
            longdesc=longdesc,
            lowsrc=lowsrc,
            src=src,
            vspace=vspace,
            width=width,
            usemap=usemap,
            **kwargs
        )
