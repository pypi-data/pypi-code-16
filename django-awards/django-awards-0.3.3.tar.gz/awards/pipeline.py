
from . import possibly_award_badge


def award_user(strategy, user=None, *args, **kwargs):
    if not user:
        return

    possibly_award_badge('social_network_linked', user=user)
