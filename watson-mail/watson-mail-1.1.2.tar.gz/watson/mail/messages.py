# -*- coding: utf-8 -*-
from email import utils, charset
from email.mime import multipart, text, application
from os import path
import re
from watson.common.imports import get_qualified_name
from watson.mail import backends

__all__ = ['Message']

TAG_REGEX = re.compile(r'<[^>]+>')


class Address(object):
    """An individual recipient that can be assigned to an email.
    """
    name = None
    email = None

    def __init__(self, email, name=None):
        self.email = email
        self.name = name

    @property
    def formatted(self):
        """Returns the formatted version of the recipient in Name <Email>
        format.
        """
        if self.name:
            return utils.formataddr((self.name, self.email))
        return self.email


class AddressList(list):
    """Subclassed list to provide for simple checking as to whether or not
    an email is in the group of addresses.
    """
    def remove(self, email):
        for recipient in self:
            if recipient.email == email:
                super(AddressList, self).remove(recipient)

    def add(self, email, name=None):
        self.append(Address(email, name))

    def __contains__(self, email):
        for adddress in self:
            if adddress.email == email:
                return True
        return False

    def __str__(self):
        addresses = [address.formatted for address in self]
        return ', '.join(addresses)


def _process_addresses(addresses):
    recipients = AddressList()
    if not addresses:
        return recipients
    if isinstance(addresses, list):
        for address in addresses:
            recipients.append(_process_address(address))
    else:
        recipients.append(_process_address(addresses))
    return recipients


def _process_address(address):
    if isinstance(address, (list, tuple)):
        name, email = address
    else:
        name = None
        email = address
    return Address(email, name)


class Recipients(object):
    """A group of recipients that an email may have.

    Attributes:
        to (AddressList): a list of people the email should go to
        cc (AddressList): a list of people who should be cc'd in
        bcc (AddressList): a list of people who should be bcc'd in
    """
    _to = None
    _cc = None
    _bcc = None

    @property
    def to(self):
        return self._to

    @to.setter
    def to(self, value):
        self._to = _process_addresses(value)

    @property
    def cc(self):
        return self._cc

    @cc.setter
    def cc(self, value):
        self._cc = _process_addresses(value)

    @property
    def bcc(self):
        return self._bcc

    @bcc.setter
    def bcc(self, value):
        self._bcc = _process_addresses(value)

    def __init__(self, to, cc=None, bcc=None):
        self.to = to
        self.cc = cc
        self.bcc = bcc


class Senders(object):
    """Who the email is coming from.

    Attributes:
        from_ (Address): the primary person sending the email
        reply_to (AddressList): who should be on the reply to
    """
    _from = None
    reply_to = None

    @property
    def from_(self):
        return self._from

    @from_.setter
    def from_(self, value):
        self._from = _process_address(value)

    def __init__(self, from_, reply_to=None):
        if not reply_to:
            reply_to = from_
        self.from_ = from_
        self.reply_to = _process_addresses(reply_to)


class Message(object):
    """Send an email via a specified backend.

    The Message class provides logical several defaults to handle the most
    common use cases. For example, if no backend is specified, it will default
    to the Sendmail backend.

    Attributes:
        backend (watson.mail.backends.abc.Base): The backend used to send the email
        recipients (watson.mail.messages.AddressList): The recipients of the email
        senders (watson.mail.messages.AddressList): The senders of the email
        subject (string): The subject of the email
        body (string): The body of the email, should be HTML
        alternative (string): The alternative body of the email, should be text
        encoding (string): The encoding for the body, defaults to utf-8
        send_as_base64 (bool): Whether or not the contents should be encoded as base64, defaults to True

    Example:

        .. code-block:: python

            from watson.mail import backends, Message

            # Multiple recipients should be in the form of a list
            # Specifying a name can be done via a tuple ('user@email.com', 'User')
            message = Message(to='user@email.com')
            message.send()

            # Sending via SMTP
            # NOTE: If 2-factor auth is enabled for gmail, you will need to
            # request an App Password from within Gmail first.
            message = Message(
                to='user@email.com',
                backend=backends.SMTP(
                    host='smtp.gmail.com',
                    port=587,
                    username='user@gmail.com',
                    password='password',
                    start_tls=True))
            message.send()
    """
    backend = None
    recipients = None
    senders = None
    subject = None
    body = None
    alternative = None
    encoding = None
    attachments = None
    send_as_base64 = True

    def __init__(
            self,
            to,
            from_=None,
            reply_to=None,
            cc=None,
            bcc=None,
            subject='',
            encoding='utf-8',
            body='',
            alternative=None,
            send_as_base64=True,
            backend=None,
            attachments=None):
        """Initialise the message.

        The only required argument to create a valid message is the to address.
        If no from address is specified it will fallback to the to address. If
        no reply_to address is specified it will fallback to the from address.

        If no backend is specified, the Sendmail backend will be used by default.

        Args:
            to (string|list|tuple): The addresses to send the email to
            from_ (string): The address to send the email from
            reply_to (string|list|tuple): The addresses that form Reply-To
            to (string|list|tuple): The addresses to cc
            bto (string|list|tuple): The addresses to bcc
            subject (string): The subject of the email
            encoding (string): The encoding for the body
            body (string): The body of the email, should be HTML
            alternative (string): The alternative body of the email, should be text
            send_as_base64 (bool): Whether or not the contents should be encoded as base64
            backend (watson.mail.backends.abc.Base): The backend used to send the email
            attachments (list): A list of files (path) to attach to the email
        """
        if not from_:
            from_ = to
        self.recipients = Recipients(to, cc, bcc)
        self.senders = Senders(from_, reply_to)
        self.subject = subject
        self.encoding = encoding
        if not backend:
            backend = backends.Sendmail()
        self.backend = backend
        self.send_as_base64 = send_as_base64
        self.body = body
        self.alternative = alternative
        self.attachments = [] if not attachments else attachments

    @property
    def prepared(self):
        """Convert the message into one that the standard library classes
        can utilize for sending.
        """
        message = multipart.MIMEMultipart('mixed')

        message['Subject'] = self.subject
        message['To'] = str(self.recipients.to)
        if self.recipients.cc:
            message['Cc'] = str(self.recipients.cc)
        if self.recipients.bcc:
            message['Bcc'] = str(self.recipients.bcc)

        message_alternative = multipart.MIMEMultipart('alternative')

        text_body = self.alternative if self.alternative else TAG_REGEX.sub(
            '', self.body.replace('<br>', "\n"))
        html_message = text.MIMEText(self.body, 'html', self.encoding)
        text_message = text.MIMEText(text_body, _charset=self.encoding)
        if not self.send_as_base64:
            self._convert_base64_to_printable(
                html_message, self.body, self.encoding)
            self._convert_base64_to_printable(
                text_message, text_body, self.encoding)
        message_alternative.attach(html_message)
        message_alternative.attach(text_message)
        for attachment in self.attachments:
            with open(attachment, 'rb') as f:
                message_attachment = application.MIMEApplication(f.read())
                filename = path.basename(attachment)
                message_attachment.add_header(
                    'Content-Disposition', 'attachment', filename=filename)
                message.attach(message_attachment)
        message.attach(message_alternative)

        return message

    def attach(self, path):
        """Attach a file to the email.

        The files name will be used as the attachment name when the email is
        sent.

        Args:
            path (string): The path to the file
        """
        self.attachments.append(path)

    def send(self):
        """Convenience method for sending via a specified backend.
        """
        if not self.backend:
            raise Exception('No backend has been set for the message.')
        self.backend.send(self)

    def _convert_base64_to_printable(self, message, body, encoding):
        _charset = charset.Charset(encoding)
        _charset.body_encoding = charset.QP
        message.replace_header('Content-Transfer-Encoding', 'quoted-printable')
        message.set_payload(body, _charset)

        return message

    def __repr__(self):
        return '<{0} to:{1} cc:{2} bcc:{3}>'.format(
            get_qualified_name(self),
            len(self.recipients.to),
            len(self.recipients.cc),
            len(self.recipients.bcc))
