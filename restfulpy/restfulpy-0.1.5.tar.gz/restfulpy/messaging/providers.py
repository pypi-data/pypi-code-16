
import smtplib
from email.mime.text import MIMEText

from mako.lookup import TemplateLookup, Template
from nanohttp import settings, LazyAttribute

from restfulpy.utils import construct_class_by_name


class Messenger(object):
    """
    The abstract base class for everyone messaging operations
    """

    def render_body(self, body, template_string=None, template_filename=None):
        if template_string:
            mako_template = Template(template_string)
        elif template_filename:
            mako_template = self.lookup.get_template(template_filename)
        else:
            mako_template = None

        if mako_template:
            return mako_template.render(**body)
        else:
            return body

    @LazyAttribute
    def lookup(self):
        return TemplateLookup(directories=settings.messaging.template_dirs, input_encoding='utf8')

    def send(self, to, subject, body, cc=None, bcc=None, template_string=None, template_filename=None, from_=None):
        raise NotImplementedError


class SmtpProvider(Messenger):

    def send(self, to, subject, body, cc=None, bcc=None, template_string=None, template_filename=None, from_=None):
        """
        Sending messages with SMTP server
        """
        body = self.render_body(body, template_string, template_filename)

        smtp_config = settings.smtp
        smtp_server = smtplib.SMTP(
            host=smtp_config.host,
            port=smtp_config.port,
            local_hostname=smtp_config.local_hostname
        )
        smtp_server.starttls()
        smtp_server.login(smtp_config.username, smtp_config.password)

        msg = MIMEText(body, 'html')
        msg['Subject'] = subject
        msg['From'] = from_
        msg['To'] = to
        if cc:
            msg['Cc'] = cc
        if bcc:
            msg['Bcc'] = bcc

        smtp_server.send_message(msg)
        smtp_server.quit()


class ConsoleMessenger(Messenger):
    def send(self, to, subject, body, cc=None, bcc=None, template_string=None, template_filename=None, from_=None):
        """
        Sending messages by email
        """

        body = self.render_body(body, template_string, template_filename)
        print(body)


def create_messenger() -> Messenger:
    return construct_class_by_name(settings.messaging.default_messenger)
