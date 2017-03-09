
from zope import schema
from zope.interface import Interface


from c2.patch.sharesettingcopy import _



class IShareSettingCopyControlPanel(Interface):
    """IShareSettingCopyControlPanel ControlPanel setting interface
    """

    is_share_copy = schema.Bool(
        required=False,
        title=_(u"Enable share copy"),
        default=True,
        )
