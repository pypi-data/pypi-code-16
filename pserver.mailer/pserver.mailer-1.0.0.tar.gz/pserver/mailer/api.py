from plone.server import configure
from plone.server.api.service import Service
from plone.server.browser import Response
from plone.server.interfaces import ISite
from pserver.mailer.interfaces import IMailer
from zope.component import queryUtility


@configure.service(context=ISite, name='@mailer', method="POST",
                   permission="mailer.SendMail")
class SendMail(Service):

    async def __call__(self):
        data = await self.request.json()
        mailer = queryUtility(IMailer)
        await mailer.send(**data)
        return Response(response={
            'messages_sent': 1
        }, status=200)
