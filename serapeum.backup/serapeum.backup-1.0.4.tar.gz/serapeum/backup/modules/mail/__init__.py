import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class Mail:
    def __init__(self, server, port, username, password, starttls=True):
        self.server = self.__start(server, port, username, password, starttls)

    def __del__(self):
        self.server.close()

    def __start(self, server, port, username, password, starttls):
        smtp_server = smtplib.SMTP(server, port)
        if starttls is True:
            smtp_server.starttls()
        smtp_server.login(username, password)
        return smtp_server

    def send(self, sender, recipient, msg_text, subject=None):
        if not subject:
            subject = 'A back-up job failed.'
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(msg_text, 'plain'))
        self.server.sendmail(sender, recipient, msg.as_string())
        return True
