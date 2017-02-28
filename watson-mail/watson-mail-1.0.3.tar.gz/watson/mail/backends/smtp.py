# -*- coding: utf-8 -*-
import smtplib
from watson.mail.backends import abc


class SMTP(abc.Base):
    """Send an email via SMTP.
    """

    host = None
    port = None
    username = None
    password = None
    use_ssl = False
    start_ttls = False
    kwargs = None
    _smtp = None

    def __init__(
            self,
            host='localhost',
            port=25,
            username=None,
            password=None,
            use_ssl=False,
            start_ttls=False,
            **kwargs):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.use_ssl = use_ssl
        self.start_ttls = start_ttls
        self.kwargs = kwargs

    @property
    def smtp_class(self):
        return smtplib.SMTP if not self.use_ssl else smtplib.SMTP_SSL

    def quit(self):
        if self._smtp:
            try:
                self._smtp.quit()
            except:
                pass
            self._smtp = None

    def send(self, message, should_quit=False, **kwargs):
        self._login()
        mail = self._smtp.sendmail(
            from_addr=message.senders.from_.email,
            to_addrs=str(message.recipients.to),
            msg=message.prepared.as_string(),
            **kwargs)
        if should_quit:
            self._smtp.quit()
            self._smtp = None
        return mail

    def _login(self):
        if not self._smtp:
            self._smtp = self.smtp_class(
                host=self.host, port=self.port, **self.kwargs)
        if self.start_ttls:
            self._smtp.ehlo()
            self._smtp.starttls()
        self._smtp.login(self.username, self.password)

    def __del__(self):
        self.quit()
