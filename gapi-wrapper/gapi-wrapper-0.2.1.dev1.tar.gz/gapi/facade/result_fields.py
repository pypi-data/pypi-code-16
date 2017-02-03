# -*- coding: utf-8 -*-
import datetime

from gapi.exceptions import APIValueError
from gapi.facade.utils import to_snake_case
from gapi.utils import to_google_camel_case

__all__ = [
    'AdwField', 'AdwBoolean', 'AdwInteger', 'AdwANSI', 'AdwUnicode',
    'AdwMoney', 'AdwDate', 'AdwANSIList', 'AdwUnicodeList',
    'AdwDict', 'AdwBids', 'AdwPercent',
]


class AdwField(object):

    def __init__(self, name, obtain_name=None, output_name=None, fake_field=False, **kwargs):
        self.name = name
        if obtain_name:
            self.obtain_name = obtain_name
        else:
            self.obtain_name = to_google_camel_case(self.name)
        self.value = None
        self.output_name = output_name
        # TODO запилить получение всех видов критериев в одном запросе
        self.fake_field = fake_field
        self.kwargs = kwargs

    def __unicode__(self):
        return u"{}: {}/{}".format(self.__class__.__name__, self.name, self.value)

    def __str__(self):
        return unicode(self)

    def extract(self, row):
        nodes = self.obtain_name.split('.')
        self.value = row
        for node in nodes:
            try:
                self.value = self.value[node]
            except (KeyError, TypeError):
                self.value = None
                return False
        return True

    def to_plain(self):
        if self.value is None:
            return None
        return self._to_plain()

    @property
    def converted_name(self):
        return to_snake_case(self.name)

    def _to_plain(self):
        raise NotImplemented()


def _get_money(value, prec):
    try:
        value = value.microAmount
    except AttributeError:  # no microAmount
        pass
    return round(int(value) / 1000000.0, prec)


class AdwBoolean(AdwField):

    def _to_plain(self):
        return self.value in ('True', True, '1', 1)


class AdwInteger(AdwField):

    def _to_plain(self):
        return int(self.value)


class AdwFloat(AdwField):

    def _to_plain(self):
        return float(self.value)


class AdwANSI(AdwField):

    def _to_plain(self):
        return str(self.value)



def _decode(value):
    import suds
    if isinstance(value, str):
        for encoding in ('utf8', 'cp1251', 'koi8_r'):  # возможные (?) кодировки
            try:
                return unicode(value, encoding=encoding)
            except UnicodeDecodeError:
                pass
    elif isinstance(value, suds.sax.text.Text):
        return unicode(value)
    return value


class AdwUnicode(AdwField):

    def _to_plain(self):
        return _decode(self.value)


class AdwDate(AdwField):
    FORMATS = ('%Y%m%d', '%Y-%m-%d')

    def _to_plain(self):
        for fmt in self.FORMATS:
            try:
                return datetime.datetime.strptime(self.value, fmt).strftime('%Y-%m-%d')
            except ValueError:  # time data '2016-05-04' does not match format '%Y%m%d'
                pass
        from gapi import GAPIException
        raise GAPIException("Time data {} does not match any formats {}".format(
            self.value,
            ','.join(self.FORMATS)
        ))


class AdwMoney(AdwField):
    PRECISION = 3

    def _to_plain(self):
        return _get_money(self.value, self.PRECISION)


class AdwANSIList(AdwField):

    def _to_plain(self):
        return map(str, self.value)


class AdwUnicodeList(AdwField):

    def _to_plain(self):
        return map(_decode, self.value)


class AdwPercent(AdwField):

    def _to_plain(self):
        return float(self.value.replace('%', ''))


class AdwDict(AdwField):

    def _to_plain(self):
        return dict(self.value)


class AdwObject(AdwField):

    def _to_plain(self):
        return self.value


class AdwBids(AdwField):
    PRECISION = 3

    def _to_plain(self):
        res = {}
        for row in self.value:
            bid = _get_money(row['bid'], prec=self.PRECISION)
            bid_type = row['Bids.Type']
            if bid_type == 'CpcBid':
                res['cpc'] = bid
                res['cpc_source'] = row['cpcBidSource']
            elif bid_type == 'CpmBid':
                res['cpm'] = bid
                res['cpm_source'] = row['cpmBidSource']
            else:
                raise APIValueError('AdwBids field: Unknown Bids.Type {}'.format(bid_type))
        return res

