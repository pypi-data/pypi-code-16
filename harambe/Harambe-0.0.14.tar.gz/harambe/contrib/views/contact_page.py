
"""
Contact Page
"""
from harambe import (Harambe,
                   _,
                   get_config,
                   url_for,
                   abort,
                   request,
                   utils,
                   flash_success,
                   flash_error,
                   flash_data,
                   get_flash_data,
                   send_mail,
                   recaptcha,
                   page_meta,
                   redirect,
                   decorators as deco,
                   exceptions)
from harambe.contrib.app_option import AppOption
import logging

__version__ = "1.0.0"
__options__ = {}


class Main(Harambe):

    app_option = AppOption(__name__)

    @classmethod
    def _register(cls, app, **kwargs):
        """ Reset some params """

        # nav
        nav = __options__.get("nav", {})
        nav.setdefault("title", "Contact")
        nav.setdefault("visible", True)
        nav.setdefault("order", 100)
        title = nav.pop("title")
        deco.nav_title.add(title, cls.index, **nav)

        # route
        kwargs["base_route"] = __options__.get("route", "/contact/")

        # App Option
        cls.app_option.init({
            "recipients": __options__.get("recipients"),
            "success_message": __options__.get("success_message", "Message sent. Thanks!")
        }, "Contact Page Options")

        # Call the register
        super(cls, cls)._register(app, **kwargs)

    @deco.route("/", methods=["GET", "POST"])
    def index(self):

        recipients = self.app_option.get("recipients") \
                     or __options__.get("recipients") \
                     or get_config("CONTACT_EMAIL")

        if not recipients:
            abort(500, "ContactPage missing email recipient")

        success_message = self.app_option.get("success_message") \
                          or __options__.get("success_message")

        return_to = __options__.get("return_to", None)
        if return_to:
            if "/" not in return_to:
                return_to = url_for(return_to)
        else:
            return_to = url_for(self)

        if request.method == "POST":
            email = request.form.get("email")
            subject = request.form.get("subject")
            message = request.form.get("message")
            name = request.form.get("name")

            try:
                if recaptcha.verify():
                    if not email or not subject or not message:
                        raise exceptions.AppError("All fields are required")
                    elif not utils.is_email_valid(email):
                        raise exceptions.AppError("Invalid email address")
                    else:
                        try:
                            send_mail(to=recipients,
                                      reply_to=email,
                                      mail_from=email,
                                      mail_subject=subject,
                                      mail_message=message,
                                      mail_name=name,
                                      template=__options__.get("template", "contact-us.txt")
                                      )
                            flash_data("ContactPage:EmailSent")
                        except Exception as ex:
                            logging.exception(ex)
                            raise exceptions.AppError("Unable to send email")
                else:
                    raise exceptions.AppError("Security code is invalid")
            except exceptions.AppError as e:
                flash_error(e.message)
            return redirect(self)

        title = __options__.get("title", _("Contact Us"))
        page_meta(title)

        fd = get_flash_data()
        return {
            "title": title,
            "email_sent": True if fd and "ContactPage:EmailSent" in fd else False,
            "success_message": success_message,
            "return_to": return_to
        }




