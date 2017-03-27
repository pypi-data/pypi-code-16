import os
import datetime
import uuid
from harambe import (Harambe, models, nav_menu, page_meta, init_app,
                         route, get_config, session, request, redirect,
                         url_for, get, post, flash, flash_data, flash_success, flash_error,
                         abort, recaptcha, storage, get_flash_data)

from flask_login import fresh_login_required
from harambe.exceptions import AppError
from harambe import utils
import json
from . import _del_cache_key
from harambe.contrib.auth import (current_user, authenticated, is_authenticated,
                                not_authenticated, accepts_admin_roles, visible_to_admins)


def main(**kwargs):

    options = kwargs.get("options", {})
    nav_kwargs = kwargs.get("nav_menu", {})

    @accepts_admin_roles
    class AppDataAdmin(Harambe):
        base_route = "/admin"
        decorators = [authenticated, accepts_admin_roles]

        @nav_menu("App Data",
                  visible=visible_to_admins,
                  order=nav_kwargs.pop("order", 100))
        @get("/app-data/")
        def index(self):
            """
            List all posts
            """
            page_meta(title="App Data")
            page = request.args.get("page", 1)

            prefs = models.AppData.query()\
                .order_by(models.AppData.key.asc())\
                .paginate(page=page, per_page=25)

            return {
                "prefs": prefs
            }

        @nav_menu("App Data", visible=False)
        @route("/app-data/<id>/")
        def get(self, id):
            pref = models.AppData.get(id)
            return {
                "pref": pref
            }

        def post(self):
            id = request.form.get("id")
            action = request.form.get("action")
            key = request.form.get("key")
            value = request.form.get("value")
            description = request.form.get("description")

            if action in ["update", "delete"]:
                pref = models.AppData.get(id)
                if not pref:
                    abort(404, "App Data doesn't exist")

                if action == "update":
                    if pref.is_editable:
                        pref.data = value
                        ns, k = pref.key.split(".", 2)
                        _del_cache_key(namespace=ns, key=k)

                    pref.update(description=description)
                    flash_success("App Data '%s' updated successfully!" % pref.key)
                elif action == "delete":
                    flash_success("App Data '%s' deleted successfully!" % pref.key)
                    return redirect(self.index)

            return redirect(self.get, id=id)

    return AppDataAdmin
