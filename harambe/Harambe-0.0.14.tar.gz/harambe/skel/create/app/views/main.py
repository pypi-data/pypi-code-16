"""
Harambe

Views

"""
from harambe import (Harambe,
                     page_meta,
                     get_config,
                     flash_success,
                     flash_error,
                     abort,
                     request,
                     url_for,
                     redirect,
                     models,
                     utils,
                     paginate,
                     decorators as deco
                     )


# ------------------------------------------------------------------------------


class Index(Harambe):
    @deco.nav_title("Home", order=1)
    def index(self):
        page_meta("Hello View!")
        return
