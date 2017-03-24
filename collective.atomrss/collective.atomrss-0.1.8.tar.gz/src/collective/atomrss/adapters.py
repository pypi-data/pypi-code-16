from Products.ATContentTypes.interfaces import IATNewsItem
from plone.app.contenttypes.interfaces import INewsItem
from Products.ATContentTypes.interfaces import IATEvent
from plone.app.contenttypes.interfaces import IEvent
from Products.CMFPlone.browser.syndication.adapters import BaseItem
from Products.CMFPlone.browser.syndication.settings import FeedSettings
from Products.CMFPlone.interfaces.syndication import IFeed
from Products.CMFPlone.interfaces.syndication import ISyndicatable
from Products.CMFPlone.interfaces.syndication import IFeedSettings
from Products.CMFPlone.browser.syndication.settings import FEED_SETTINGS_KEY
from zope.annotation.interfaces import IAnnotations
from zope.component import adapts
from zope.interface import implements


class AtomFeedSettings(FeedSettings):
    """ Change default value for feed : atom.xml is first and render_body True
    """
    implements(IFeedSettings)
    adapts(ISyndicatable)

    def __init__(self, context):
        super(AtomFeedSettings, self).__init__(context)
        annotations = IAnnotations(context)

        if 'render_body' not in self._metadata.keys():
            self._metadata['render_body'] = True
            annotations[FEED_SETTINGS_KEY] = self._metadata
        if 'feed_types' not in self._metadata.keys():
            self._metadata['feed_types'] = (u'atom.xml', u'RSS', u'rss.xml')
            annotations[FEED_SETTINGS_KEY] = self._metadata


class NewsFeedItem(BaseItem):
    adapts(INewsItem, IFeed)

    @property
    def image_obj(self):
        image_field = 'image'
        field = getattr(self.context, image_field)
        # Check if there is a leadImage and if it's not empty
        if field is not None and field.data:
            scaling = 'preview'
            img_url = "{0}/@@images/{1}/{2}".format(
                self.context.absolute_url(),
                image_field,
                scaling)
            img_size = field.size
            img_type = field.contentType
            img_title = field.filename
            return {
                'url': img_url,
                'size': img_size,
                'type': img_type,
                'title': img_title
            }
        else:
            return False

    @property
    def image_url(self):
        """ backward compatibilites """
        image_obj = self.image_obj()
        if not image_obj:
            return False
        else:
            return image_obj.get('url')


class ATNewsFeedItem(BaseItem):
    adapts(IATNewsItem, IFeed)

    @property
    def image_url(self):
        image_field = 'image'
        scaling = 'preview'
        return "{0}/{1}_{2}".format(
            self.context.absolute_url(),
            image_field,
            scaling)

    @property
    def image_obj(self):
        """ Used to dexterity content types """
        return False

class EventFeedItem(BaseItem):
    adapts(IEvent, IFeed)

    @property
    def startdate(self):
        return getattr(self.context, 'start', '')

    @property
    def enddate(self):
        return getattr(self.context, 'end', '')

    @property
    def contactname(self):
        return getattr(self.context, 'contact_name', '')

    @property
    def contactemail(self):
        return getattr(self.context, 'contact_email', '')

    @property
    def contactphone(self):
        return getattr(self.context, 'contact_phone', '')

    @property
    def location(self):
        return self.context.location

    @property
    def eventurl(self):
        return getattr(self.context, 'event_url', '')

    @property
    def image_obj(self):
        image_field = 'image'
        field = getattr(self.context, image_field)
        # Check if there is a leadImage and if it's not empty
        if field is not None and field.data:
            scaling = 'preview'
            img_url = "{0}/@@images/{1}/{2}".format(
                self.context.absolute_url(),
                image_field,
                scaling)
            img_size = field.size
            img_type = field.contentType
            img_title = field.filename
            return {
                'url': img_url,
                'size': img_size,
                'type': img_type,
                'title': img_title
            }
        else:
            return False

    @property
    def image_url(self):
        """ backward compatibilites """
        image_obj = self.image_obj()
        if not image_obj:
            return False
        else:
            return image_obj.get('url')

class ATEventFeedItem(BaseItem):
    adapts(IATEvent, IFeed)

    @property
    def startdate(self):
        return str(self.context.startDate)

    @property
    def enddate(self):
        return str(self.context.endDate)

    @property
    def contactname(self):
        return self.context.contact_name()

    @property
    def contactemail(self):
        return self.context.contact_email()

    @property
    def contactphone(self):
        return self.context.contact_phone()

    @property
    def location(self):
        return self.context.location

    @property
    def eventurl(self):
        return self.context.event_url()

    @property
    def image_url(self):
        image_field = 'leadImage'
        field = self.context.getField(image_field)
        # Check if there is a leadImage and if it's not empty
        if field is not None:
            value = field.get(self.context)
            if not bool(value):
                return False
        else:
            return False
        scaling = 'preview'
        return "{0}/{1}_{2}".format(
            self.context.absolute_url(),
            image_field,
            scaling)

    @property
    def image_obj(self):
        """ Used to dexterity content types """
        return False
