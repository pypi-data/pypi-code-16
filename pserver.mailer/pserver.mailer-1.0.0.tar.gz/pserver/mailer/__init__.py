# -*- coding: utf-8 -*-
from plone.server import configure

app_settings = {
    "mailer": {
        "default_sender": "foo@bar.com",
        "endpoints": {
            "default": {
                "type": "smtp",
                "host": "localhost",
                "port": 25
            }
        },
        "debug": False,
        "utility": "pserver.mailer.utility.MailerUtility",
        "use_html2text": True,
        "domain": None
    }
}


configure.permission(id="mailer.SendMail", title="Request subscription")
configure.grant(permission="mailer.SendMail", role="plone.SiteAdmin")


def includeme(root, settings):
    utility = settings.get('mailer', {}).get('utility',
                                             app_settings['mailer']['utility'])
    root.add_async_utility({
        "provides": "pserver.mailer.interfaces.IMailer",
        "factory": utility,
        "settings": settings.get('mailer', {})
    })

    configure.scan('pserver.mailer.api')
