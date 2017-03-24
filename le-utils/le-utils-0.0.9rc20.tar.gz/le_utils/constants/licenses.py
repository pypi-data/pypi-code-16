from gettext import gettext as _

""" License Constants """
CC_BY = "CC BY"
CC_BY_SA = "CC BY-SA"
CC_BY_ND = "CC BY-ND"
CC_BY_NC = "CC BY-NC"
CC_BY_NC_SA = "CC BY-NC-SA"
CC_BY_NC_ND = "CC BY-NC-ND"
ALL_RIGHTS_RESERVED = "All Rights Reserved"
PUBLIC_DOMAIN = "Public Domain"

choices = (
    (CC_BY, _("CC BY (Attribution)")),
    (CC_BY_SA, _("CC BY-SA (Attribution-ShareAlike)")),
    (CC_BY_ND, _("CC BY-ND (Attribution-NoDerivs)")),
    (CC_BY_NC, _("CC BY-NC (Attribution-NonCommercial)")),
    (CC_BY_NC_SA, _("CC BY-NC-SA (Attribution-NonCommercial-ShareAlike)")),
    (CC_BY_NC_ND, _("CC BY-NC-ND (Attribution-NonCommercial-NoDerivs)")),
    (ALL_RIGHTS_RESERVED, _("All Rights Reserved")),
    (PUBLIC_DOMAIN, _("Public Domain")),
)