import reversion

from .story import Story


@reversion.register(follow=['story_ptr'])
class Debt(Story):
    ident = 'D'
    typename = 'Debt'
    api_detail_name = 'debt-detail'
    api_list_name = 'debt-list'
