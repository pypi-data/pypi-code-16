from welcome import Welcome

__all__ = ['ACTIONS']

ACTIONS = {
    'raid.welcome':Welcome().on_msg
}
