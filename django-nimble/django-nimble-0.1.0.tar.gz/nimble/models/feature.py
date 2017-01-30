import reversion

from .story import Story


@reversion.register(follow=['story_ptr'])
class Feature(Story):
    ident = 'F'
    typename = 'Feature'
    api_detail_name = 'feature-detail'
    api_list_name = 'feature-list'
