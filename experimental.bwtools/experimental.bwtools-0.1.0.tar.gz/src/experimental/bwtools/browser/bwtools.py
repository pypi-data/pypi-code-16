# coding=utf-8
from json import dumps
from logging import getLogger
from plone import api
from plone.app.layout.viewlets.common import ViewletBase
from plone.memoize import ram
from plone.memoize.view import memoize
from Products.Five.browser import BrowserView
from time import time


logger = getLogger(__name__)


class View(BrowserView):
    ''' Dump the cookie into json and expose helper methods

    What is called latency here is the time needed to download a very small
    file

    The thresholds are calculated using a regular 3G connection as a reference
    '''
    _cookie_name = '_bw'
    _latency_max_threshold = .300  # s
    _bandwidth_min_threshold = 800000  # bit/s

    @property
    def cookie(self):
        ''' Look up for the cookie in the request
        '''
        return self.request.cookies.get(self._cookie_name, '')

    def expire_cookie(self):
        ''' Expire the cookie
        '''
        self.request.response.expireCookie(
            self._cookie_name,
            path='/',
        )

    @property
    @memoize
    def cookiedict(self):
        ''' Look up for the cookie in the request
        '''
        value = self.cookie
        if not value:
            return {}
        try:
            delta0, size0, delta100, size100 = map(float, value.split('|'))
            delta0 = delta0 / 1000  # ms -> s
            delta100 = delta100 / 1000  # ms -> s
            size0 = size0 * 8
            size100 = size100 * 8
            if (delta100 - delta0) > 0:
                bandwidth = (size100 - size0) / (delta100 - delta0)  # bit/s
            else:
                bandwidth = 1.e9
        except:  # noqa
            logger.warning(repr(value))
            delta0, size0, delta100, size100 = (0, 0, 0, 0,)
            bandwidth = 0
        return {
            'bandwidth': bandwidth,
            'delta0': delta0,
            'size0': size0,
            'delta100': delta100,
            'size100': size100,
        }

    @property
    @memoize
    def quality(self):
        ''' Check the network quality and rate it as an integer.

        Your application must know what to do with this index.

        You may want to override this function completely if you need it
        '''
        cookiedict = self.cookiedict
        if not cookiedict:
            # When we have no info assume everything is good
            return 1
        if cookiedict['bandwidth'] < self._bandwidth_min_threshold:
            return 0
        if cookiedict['delta0'] > self._latency_max_threshold:
            return 0
        return 1

    def expire_and_redirect(self):
        ''' Expires the cookie, show a message and return to the context view
        '''
        self.expire_cookie()
        api.portal.show_message(
            'Cookie %r removed' % self._cookie_name,
            self.request,
        )
        return self.request.response.redirect(self.context.absolute_url())

    def show_and_redirect(self):
        ''' Show the cookie contents and redirect
        '''
        response = self.cookiedict.copy()
        if not response:
            msg = 'Not enough information yet'
        else:
            msg = 'Estimated BW: %dKb/s. MDT %fs' % (
                response['bandwidth']/1024,
                response['delta0'],
            )
        api.portal.show_message(
            msg,
            self.request,
        )
        return self.request.response.redirect(self.context.absolute_url())

    def __call__(self):
        ''' Return the jsonified cookie
        '''
        self.request.response.setHeader(
            'Content-type',
            'application/json; charset=utf-8'
        )
        response = self.cookiedict.copy()
        response['quality'] = self.quality
        return dumps(response)


def _log_cache(cls, self, ip, userid, cookie):
    ''' Do not over feed the logs
    '''
    return repr((
        ip,
        cookie,
        userid,
        time() // 300,
    ))


class CheckViewlet(ViewletBase):
    ''' Check the viewlet
    '''
    @ram.cache(_log_cache)
    def log(self, ip, userid, cookie):
        ''' Write info info about your customer
        '''
        logger.info('%s %s %s', ip, userid, cookie)

    def update(self):
        ''' Log the cookie if found
        '''
        value = self.request.cookies.get('_bw', '')
        if value:
            ip = (
                self.request.get('HTTP_X_FORWARDED_FOR') or
                self.request.get('REMOTE_ADDR', None)
            )
            userid = api.user.get_current().getId() or 'anonymous'
            if ip:
                self.log(ip, userid, value)
        return super(CheckViewlet, self).update()
