from redturtle.smartlink.interfaces import ISmartLink
from plone.indexer.decorator import indexer


@indexer(ISmartLink)
def Title(object, **kw):
    internal = object.getInternalLink()
    # the string field macron in edit form calls the accessor method,
    # instead to take value from the field
    if internal and object.check_proxy_status():
        return internal.Title()

    return object.getField('title').get(object)
