
from Acquisition import aq_inner, aq_parent, aq_base
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from c2.patch.sharesettingcopy.controlpanel.interfaces import IShareSettingCopyControlPanel

def _remove_owner_role(d):
    for u, r in d.items():
        if "Owner" in r:
            r = list(set(r) - {"Owner"})
        if r:
            yield (u, r)

def copy_permision(event):
    registry = getUtility(IRegistry)
    try:
        settings = registry.forInterface(IShareSettingCopyControlPanel)
        is_share_copy = settings.is_share_copy
    except:
        return None
    if is_share_copy:
        obj = event.original
        new_obj = event.object
        new_obj.__ac_local_roles__ = dict(_remove_owner_role(getattr(aq_base(obj), '__ac_local_roles__', {})))
        new_obj.__ac_local_roles_block__ = getattr(aq_base(obj), '__ac_local_roles_block__', None)

