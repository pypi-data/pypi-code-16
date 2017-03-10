
from var import VarMixIn
from poll import PollMixIn
from widget import WidgetMixIn
from classutils.observer import ObserverMixIn


class AllMixIn(WidgetMixIn, VarMixIn, PollMixIn, ObserverMixIn):

    def __init__(self,
                 *args,
                 **kwargs):

        super(AllMixIn, self).__init__(*args, **kwargs)
