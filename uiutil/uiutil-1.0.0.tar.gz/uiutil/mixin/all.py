
from var import VarMixIn
from poll import PollMixIn
from widget import WidgetMixIn
from classutils.observer import ObserverMixIn


class AllMixIn(WidgetMixIn, VarMixIn, PollMixIn, ObserverMixIn):
    pass
